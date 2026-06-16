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
    value: 'backlog',
    icon: HelpCircle,
  },
  {
    label: '待办',
    value: 'pending',
    icon: Circle,
  },
  {
    label: '进行中',
    value: 'in_progress',
    icon: Timer,
  },
  {
    label: '已完成',
    value: 'completed',
    icon: CheckCircle,
  },
  {
    label: '已取消',
    value: 'cancelled',
    icon: CircleOff,
  },
]

export const priorities = [
  {
    label: '低',
    value: '1',
    icon: ArrowDown,
  },
  {
    label: '中',
    value: '2',
    icon: ArrowRight,
  },
  {
    label: '高',
    value: '3',
    icon: ArrowUp,
  },
  {
    label: '紧急',
    value: '4',
    icon: AlertCircle,
  },
]
