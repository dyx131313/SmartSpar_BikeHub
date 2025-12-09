import { useAuthStore } from '@/stores/auth-store'
import { Button } from '@/components/ui/button'
import { PlusIcon } from '@radix-ui/react-icons'
import { useFeedback } from './feedback-provider'

export function FeedbackPrimaryButtons() {
  const { setOpen } = useFeedback()
  const { user } = useAuthStore((state) => state.auth)
  
  // 所有人都可以创建反馈
  return (
    <div className='flex gap-2'>
      <Button onClick={() => setOpen('create')} className='space-x-1'>
        <span>提交反馈</span>
        <PlusIcon />
      </Button>
    </div>
  )
}



