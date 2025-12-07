import { getCookie } from './cookies'
import { useAuthStore } from '@/stores/auth-store'
import { ACCESS_TOKEN_COOKIE } from '@/lib/config'

export const API_BASE = import.meta.env.VITE_API_BASE ?? ''

function readTokenFromCookie(): string {
  try {
    const v = getCookie(ACCESS_TOKEN_COOKIE)
    if (!v) return ''
    const s = String(v).trim()
    if (!s || s === 'null' || s === 'undefined') return ''
    // 仅在明显是 JSON 时解析
    if ((s.startsWith('{') && s.endsWith('}')) || (s.startsWith('[') && s.endsWith(']')) || (s.startsWith('"') && s.endsWith('"'))) {
      try { return JSON.parse(s) } catch { /* fallthrough */ }
    }
    return s
  } catch {
    return ''
  }
}

export function readToken(): string {
  try {
    const storeToken = useAuthStore.getState()?.auth?.accessToken
    if (storeToken && storeToken !== 'null' && storeToken !== 'undefined') return storeToken
  } catch { }
  const fromCookie = readTokenFromCookie()
  if (fromCookie) return fromCookie
  try {
    const ls = typeof localStorage !== 'undefined' ? localStorage.getItem('access_token') : ''
    if (ls && ls !== 'null' && ls !== 'undefined') return ls
  } catch { }
  return ''
}

const IS_DEV = import.meta.env.DEV ?? false

function buildUrl(path: string) {
  if (/^https?:\/\//.test(path)) return path
  return IS_DEV ? path : `${API_BASE}${path}`
}

async function fetchWithAuth(url: string, options: RequestInit = {}, retry = true) {
  const token = readToken()
  const headers = { ...(options.headers as Record<string, string> || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(url, { ...options, headers, credentials: 'include' })

  if (res.status === 401 && retry) {
    try {
      // 后端如果提供 refresh 接口并使用 HttpOnly refresh cookie，这里会带上 cookie
      const refreshRes = await fetch(buildUrl('/api/auth/refresh'), {
        method: 'POST',
        credentials: 'include',
      })
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json().catch(() => ({}))
        const newToken = refreshData?.access_token ?? refreshData?.token ?? ''
        if (newToken) {
          useAuthStore.getState().auth.setAccessToken?.(newToken)
          try { localStorage.setItem('access_token', newToken) } catch { }
          return fetchWithAuth(url, options, false)
        }
      }
    } catch {
      // ignore and fall through to return original 401
    }
  }

  return res
}

export async function apiPost(path: string, body: any = null) {
  const url = buildUrl(path)
  console.log('API POST:', url, body)
  const res = await fetchWithAuth(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  // 尝试读取响应体，即使对于 500 错误
  let data
  try {
    data = await res.json()
  } catch {
    data = { error: '服务器返回了无法解析的响应' }
  }

  if (!res.ok) {
    console.error('API Error:', {
      url,
      status: res.status,
      statusText: res.statusText,
      data
    })

    const err: any = new Error(data?.error || data?.message || res.statusText || 'Request failed')
    err.status = res.status
    err.data = data
    err.url = url
    if (res.status === 401) {
      useAuthStore.getState().auth.reset?.()
    }
    throw err
  }
  return data
}

export async function apiGet(path: string) {
  const url = buildUrl(path)
  const res = await fetchWithAuth(url, { method: 'GET' })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err: any = new Error(data?.error || data?.message || 'Request failed')
    err.status = res.status
    err.data = data
    if (res.status === 401) {
      useAuthStore.getState().auth.reset?.()
    }
    throw err
  }
  return data
}

export async function apiPut(path: string, body: any) {
  const url = buildUrl(path)
  // console.log('apiPut url:', url)
  const res = await fetchWithAuth(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err: any = new Error(data?.error || data?.message || 'Request failed')
    err.status = res.status
    err.data = data
    if (res.status === 401) {
      useAuthStore.getState().auth.reset?.()
    }
    throw err
  }
  return data
}

export async function apiDelete(path: string) {
  const url = buildUrl(path)
  const res = await fetchWithAuth(url, { method: 'DELETE' })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err: any = new Error(data?.error || data?.message || 'Request failed')
    err.status = res.status
    err.data = data
    if (res.status === 401) {
      useAuthStore.getState().auth.reset?.()
    }
    throw err
  }
  return data
}

// 导出统一的API对象以供聊天模块使用
export const api = {
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete
}