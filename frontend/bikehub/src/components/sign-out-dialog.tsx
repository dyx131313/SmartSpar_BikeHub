import { useNavigate, useLocation } from '@tanstack/react-router'
import { useAuthStore } from '@/stores/auth-store'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { apiPost } from '@/lib/api' // 新增导入

interface SignOutDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function SignOutDialog({ open, onOpenChange }: SignOutDialogProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { auth } = useAuthStore()

  const handleSignOut = async () => {
    // Preserve current location for redirect after sign-in
    const currentPath = typeof window !== 'undefined' ? window.location.href : '/'

    try {
      // 调用后端登出接口（若后端需要鉴权，会走 apiPost 的鉴权逻辑）
      await apiPost('/api/auth/logout', {}).catch(() => {})
    } catch {
      // 忽略后端异常，仍然清理前端状态
    } finally {
      // 清理前端状态与持久化
      try { auth.reset?.() } catch {}
      try { localStorage.removeItem('access_token') } catch {}
      // 跳转到登录页并带上重定向参数
      navigate({
        to: '/sign-in-2',
        search: { redirect: currentPath },
        replace: true,
      })
      // 关闭 dialog
      onOpenChange(false)
    }
  }

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      title='登出'
      desc='您确定要登出吗？您需要重新登录才能访问您的账户。'
      confirmText='登出'
      destructive
      handleConfirm={handleSignOut}
      className='sm:max-w-sm'
    />
  )
}