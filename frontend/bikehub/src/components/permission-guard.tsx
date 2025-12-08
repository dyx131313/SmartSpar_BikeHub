import { ReactNode } from 'react'
import { useAuthStore } from '@/stores/auth-store'

interface PermissionGuardProps {
  children: ReactNode
  roles: string[] // 允许的角色列表
  fallback?: ReactNode // 无权限时显示的内容（可选）
}

export function PermissionGuard({ roles, children, fallback = null }: PermissionGuardProps) {
  const user = useAuthStore((s) => s.auth?.user)

  if (!user) {
    return <>{fallback}</>
  }

  // 兼容处理：user.role 可能是字符串或字符串数组
  const userRoles = Array.isArray(user.role) 
    ? user.role 
    : typeof user.role === 'string' 
      ? [user.role] 
      : []

  // 检查用户是否有任何一个允许的角色
  const hasPermission = roles.some(role => userRoles.includes(role))

  if (!hasPermission) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
