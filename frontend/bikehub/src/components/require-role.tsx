import { ReactNode } from 'react'
import { Navigate } from '@tanstack/react-router'
import { useAuthStore } from '@/stores/auth-store'
import { RequireAuth } from './require-auth'

interface RequireRoleProps {
  children: ReactNode
  roles: string[]
  fallbackPath?: string
}

function RoleCheck({ children, roles, fallbackPath = '/' }: RequireRoleProps) {
  const user = useAuthStore((s) => s.auth?.user)

  // 此时 RequireAuth 应该已经确保 user 存在了
  if (!user) {
    return null // Should not happen if wrapped in RequireAuth
  }

  // 兼容处理：user.role 可能是字符串或字符串数组
  const userRoles = Array.isArray(user.role) 
    ? user.role 
    : typeof user.role === 'string' 
      ? [user.role] 
      : []

  const hasPermission = roles.some(role => userRoles.includes(role))

  if (!hasPermission) {
    return <Navigate to={fallbackPath} replace />
  }

  return <>{children}</>
}

export function RequireRole(props: RequireRoleProps) {
  return (
    <RequireAuth>
      <RoleCheck {...props} />
    </RequireAuth>
  )
}
