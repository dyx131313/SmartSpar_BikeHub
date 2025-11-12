import { getCookie } from '@/lib/cookies'

export const API_BASE = import.meta.env.VITE_API_BASE ?? ''
const TOKEN_COOKIE = 'thisisjustarandomstring'

function readTokenFromCookie() {
  try {
    const v = getCookie(TOKEN_COOKIE)
    return v ? JSON.parse(v) : ''
  } catch {
    return ''
  }
}

export async function apiPost(path: string, body: any) {
  const url = `${API_BASE}${path}`
  const token = readTokenFromCookie()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
    credentials: 'include',
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err: any = new Error(data?.message ?? 'Request failed')
    err.status = res.status
    err.data = data
    throw err
  }
  return data
}

export async function apiGet(path: string) {
  const url = `${API_BASE}${path}`
  const token = readTokenFromCookie()
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(url, { credentials: 'include', headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err: any = new Error(data?.message ?? 'Request failed')
    err.status = res.status
    err.data = data
    throw err
  }
  return data
}