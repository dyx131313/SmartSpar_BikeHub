import { useAuthStore } from '@/stores/auth-store'
import { Button } from '@/components/ui/button'
import { PlusIcon } from '@radix-ui/react-icons'
import { useFeedback } from './feedback-provider'

export function FeedbackPrimaryButtons() {
  const { setOpen } = useFeedback()
  const { user } = useAuthStore((state) => state.auth)

  const userRoles = Array.isArray(user?.role) ? user?.role : user?.role ? [user.role] : []
  const isNormalUser = userRoles.includes('user')

  if (!isNormalUser) return null

  return (
    <div className='flex gap-2'>
      <Button onClick={() => setOpen('create')} className='space-x-1'>
        <span>提交反馈</span>
        <PlusIcon />
      </Button>
    </div>
  )
}



