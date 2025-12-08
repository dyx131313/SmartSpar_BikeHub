import {
  CheckCircledIcon,
  CrossCircledIcon,
  QuestionMarkCircledIcon,
  StopwatchIcon,
} from '@radix-ui/react-icons'

export const feedbackStatuses = [
  {
    value: 'pending',
    label: '待处理',
    icon: QuestionMarkCircledIcon,
  },
  {
    value: 'processing',
    label: '处理中',
    icon: StopwatchIcon,
  },
  {
    value: 'resolved',
    label: '已解决',
    icon: CheckCircledIcon,
  },
  {
    value: 'closed',
    label: '已关闭',
    icon: CrossCircledIcon,
  },
]

export const feedbackCategories = [
  {
    value: 'user_feedback',
    label: '用户反馈',
  },
  {
    value: 'dispatcher_issue',
    label: '调度异常',
  },
]



