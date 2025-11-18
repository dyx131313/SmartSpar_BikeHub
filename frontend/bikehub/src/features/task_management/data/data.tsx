import {
  ArrowDown,
  ArrowRight,
  ArrowUp,
  Circle,
  CheckCircle,
  AlertCircle,
  Timer,
  HelpCircle,
  CircleOff,
} from 'lucide-react'

export const labels = [
  {
    value: 'bug',
    label: 'Bug',
  },
  {
    value: 'feature',
    label: 'Feature',
  },
  {
    value: 'documentation',
    label: 'Documentation',
  },
]

export const statuses = [
  {
    label: '积压',
    value: '积压' as const,
    icon: HelpCircle,
  },
  {
    label: '待办',
    value: '待办' as const,
    icon: Circle,
  },
  {
    label: '正在进行',
    value: '正在进行' as const,
    icon: Timer,
  },
  {
    label: '已完成',
    value: '已完成' as const,
    icon: CheckCircle,
  },
  {
    label: '已取消',
    value: '已取消' as const,
    icon: CircleOff,
  },
]

export const priorities = [
  {
    label: '低',
    value: '低' as const,
    icon: ArrowDown,
  },
  {
    label: '中',
    value: '中' as const,
    icon: ArrowRight,
  },
  {
    label: '高',
    value: '高' as const,
    icon: ArrowUp,
  },
  {
    label: '紧急',
    value: '紧急' as const,
    icon: AlertCircle,
  },
]
