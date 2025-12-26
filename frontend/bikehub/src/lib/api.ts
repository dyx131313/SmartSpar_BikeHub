import { getCookie } from './cookies'
import { useAuthStore } from '@/stores/auth-store'
import { ACCESS_TOKEN_COOKIE } from '@/lib/config'

export const API_BASE = import.meta.env.VITE_API_BASE ?? ''
// 静态资源基础地址（可单独配置）；未设置时走当前站点域名
const STATIC_BASE = import.meta.env.VITE_STATIC_BASE ?? ''

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
  if (IS_DEV && API_BASE) {
    return `${API_BASE}${path}`
  }
  return IS_DEV ? `http://localhost:5000${path}` : `${API_BASE}${path}`
}

function buildStaticUrl(path: string) {
  // 构建静态资源URL（头像等），优先保持相对路径/当前域，避免写死 localhost
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path

  let normalizedPath = path.startsWith('/') ? path : `/${path}`
  
  // 【新增逻辑】如果路径是以 /uploads 开头但漏了 /static，自动补齐
  if (normalizedPath.startsWith('/uploads/') && !normalizedPath.startsWith('/static/')) {
    normalizedPath = `/static${normalizedPath}`
  }

  // 优先使用当前页面域名，其次可选的 STATIC_BASE
  const base = STATIC_BASE || (typeof window !== 'undefined' ? window.location.origin : '')

  // 规范化拼接，避免重复斜杠
  if (base) {
    const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base
    return `${normalizedBase}${normalizedPath}`
  }

  // 若无基础域名配置，返回相对路径（适用于同源部署）
  return normalizedPath
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

  let headers: Record<string, string> = {}
  let requestBody: any = body

  // 如果是 FormData（文件上传），不要设置 Content-Type，让浏览器自动设置
  if (body instanceof FormData) {
    // 移除 Content-Type 头，让浏览器自动生成正确的 boundary
    // headers['Content-Type'] = 'multipart/form-data'
  } else {
    headers['Content-Type'] = 'application/json'
    requestBody = JSON.stringify(body)
  }

  const res = await fetchWithAuth(url, {
    method: 'POST',
    headers,
    body: requestBody,
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
  console.log('DELETE 请求:', {
    path,
    url: buildUrl(path),
    apiBase: import.meta.env.VITE_API_BASE,
    isDev: import.meta.env.DEV
  })
  const res = await fetchWithAuth(url, { method: 'DELETE' })
  console.log('DELETE 响应:', {
    status: res.status,
    statusText: res.statusText,
    url: res.url
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

export async function apiUpload(path: string, formData: FormData) {
  const url = buildUrl(path)
  const res = await fetchWithAuth(url, {
    method: 'POST',
    body: formData,
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
// 导出统一的API对象以供聊天模块使用
export const api = {
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete
}

// 导出buildStaticUrl函数
export { buildStaticUrl }
