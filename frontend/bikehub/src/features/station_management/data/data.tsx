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
    label: 'Backlog',
    value: 'backlog' as const,
    icon: HelpCircle,
  },
  {
    label: 'Todo',
    value: 'todo' as const,
    icon: Circle,
  },
  {
    label: 'In Progress',
    value: 'in progress' as const,
    icon: Timer,
  },
  {
    label: 'Done',
    value: 'done' as const,
    icon: CheckCircle,
  },
  {
    label: 'Canceled',
    value: 'canceled' as const,
    icon: CircleOff,
  },
]

export const priorities = [
  {
    label: 'Low',
    value: 'low' as const,
    icon: ArrowDown,
  },
  {
    label: 'Medium',
    value: 'medium' as const,
    icon: ArrowRight,
  },
  {
    label: 'High',
    value: 'high' as const,
    icon: ArrowUp,
  },
  {
    label: 'Critical',
    value: 'critical' as const,
    icon: AlertCircle,
  },
]

export const station_type = [
  {
    label: '食堂',
    value: 'canteen' as const,
  },
  {
    label: '教学楼',
    value: 'teaching_building' as const,
  },
  {
    label: '图书馆',
    value: 'library' as const,
  },
  {
    label: '宿舍',
    value: 'dormitory' as const,
  },
  {
    label: '大门',
    value: 'gate' as const,
  },
  {
    label: '其他',
    value: 'other' as const,
  },

]
