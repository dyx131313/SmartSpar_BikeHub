import { type ReactNode, useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { toast } from 'sonner'
import { useAuthStore } from '@/stores/auth-store'
import { apiGet, readToken } from '@/lib/api'

export function RequireAuth({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.auth?.user)
  const setUser = useAuthStore((s) => s.auth?.setUser)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    let mounted = true
    async function check() {
      if (user) {
        if (mounted) setChecking(false)
        return
      }
      if (!readToken()) {
        if (!mounted) return
        const redirect = typeof window !== 'undefined' ? window.location.pathname + window.location.search + window.location.hash : '/'
        toast?.info?.('请先登录以继续')
        navigate({ to: '/sign-in-2', search: { redirect }, replace: true })
        return
      }
      try {
        const resp = await apiGet('/api/users/profile').catch(() => null)
        const u = resp?.data ?? resp?.user ?? resp ?? null
        if (u) {
          setUser?.(u)
          if (mounted) setChecking(false)
          return
        }
      } catch {
        // ignore
      }
      if (!mounted) return
      const redirect = typeof window !== 'undefined' ? window.location.pathname + window.location.search + window.location.hash : '/'
      toast?.info?.('请先登录以继续')
      navigate({ to: '/sign-in-2', search: { redirect }, replace: true })
    }
    check()
    return () => { mounted = false }
  }, [user, navigate, setUser])

  if (checking) return null // 或者 return <Spinner /> 显示加载中
  return <>{children}</>
}
