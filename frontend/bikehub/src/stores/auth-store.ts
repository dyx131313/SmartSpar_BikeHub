import { create } from 'zustand'
import { getCookie, setCookie, removeCookie } from '@/lib/cookies'
import { ACCESS_TOKEN_COOKIE } from '@/lib/config'


interface AuthUser {
  accountNo: string
  email: string
  role: string[]
  exp: number
}

interface AuthState {
  auth: {
    user: AuthUser | null
    setUser: (user: AuthUser | null) => void
    accessToken: string
    setAccessToken: (accessToken: string) => void
    resetAccessToken: () => void
    reset: () => void
  }
}

function parseCookieValue(v?: string | undefined): string {
  if (!v) return ''
  const s = String(v).trim()
  if (!s || s === 'null' || s === 'undefined') return ''
  // 仅在明显是 JSON 时尝试解析，避免对 JWT 原文误 parse
  if ((s.startsWith('{') && s.endsWith('}')) || (s.startsWith('[') && s.endsWith(']')) || (s.startsWith('"') && s.endsWith('"'))) {
    try {
      return JSON.parse(s)
    } catch {
      // fallthrough
    }
  }
  return s
}

export const useAuthStore = create<AuthState>()((set) => {
  // 优先读取配置名的 cookie，若不存在则尝试迁移 legacy 名称
  const newCookie = getCookie(ACCESS_TOKEN_COOKIE)
  let initToken = parseCookieValue(newCookie)
  return {
    auth: {
      user: null,
      setUser: (user) =>
        set((state) => ({ ...state, auth: { ...state.auth, user } })),
      accessToken: initToken,
      setAccessToken: (accessToken) =>
        set((state) => {
          // 统一写入原始字符串（不要强制 JSON.stringify）
          const raw = typeof accessToken === 'string' ? accessToken : String(accessToken)
          try {
            setCookie(ACCESS_TOKEN_COOKIE, raw)
          } catch {
            // ignore set cookie error
          }
          return { ...state, auth: { ...state.auth, accessToken } }
        }),
      resetAccessToken: () =>
        set((state) => {
          // 删除新/旧 cookie，保证兼容清理
          try { removeCookie(ACCESS_TOKEN_COOKIE) } catch {}
          return { ...state, auth: { ...state.auth, accessToken: '' } }
        }),
      reset: () =>
        set((state) => {
          try { removeCookie(ACCESS_TOKEN_COOKIE) } catch {}
          return {
            ...state,
            auth: { ...state.auth, user: null, accessToken: '' },
          }
        }),
    },
  }
})