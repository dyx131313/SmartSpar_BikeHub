import { Shield, UserCheck, MapPin, Wrench } from 'lucide-react'
import { type UserStatus } from './schema'
import { M } from 'node_modules/@clerk/clerk-react/dist/useAuth-BAhNYMIt.d.mts'

export const callTypes = new Map<UserStatus, string>([
  ['已激活', 'bg-teal-100/30 text-teal-900 dark:text-teal-200 border-teal-200'],
  ['未激活', 'bg-neutral-300/40 border-neutral-300'],
  // ['已邀请', 'bg-sky-200/40 text-sky-900 dark:text-sky-100 border-sky-300'],
  [
    '被暂停',
    'bg-destructive/10 dark:bg-destructive/50 text-destructive dark:text-primary border-destructive/10',
  ],
])

export const status = [
  {
    label: '已激活',
    value: '已激活',
  },
  {
    label: '未激活',
    value: '未激活',
  },
  // {
  //   label: '已邀请',
  //   value: '已邀请',
  // },
  {
    label: '被暂停',
    value: '被暂停',
  },
] as const

export const roles = [
  {
    label: '管理员',
    value: 'admin',
    icon: Shield,
  },
  {
    label: '普通用户',
    value: 'user',
    icon: UserCheck,
  },
  {
    label: '调度员',
    value: 'dispatcher',
    icon: MapPin,
  },
  {
    label: '运维员',
    value: 'maintenance',
    icon: Wrench,
  },
] as const
