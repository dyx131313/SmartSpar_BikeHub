import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { FeedbackDialogs } from './components/feedback-dialogs'
import { FeedbackPrimaryButtons } from './components/feedback-primary-buttons'
import { FeedbackProvider } from './components/feedback-provider'
import { FeedbackTable } from './components/feedback-table'
import { RequireAuth } from '@/components/require-auth'
import { useQuery } from '@tanstack/react-query'
import { getFeedbacks } from './api'
import { ConfigDrawer } from '@/components/config-drawer'

export default function Feedback() {
  const { data: feedbackData } = useQuery({
    queryKey: ['feedbacks'],
    queryFn: () => getFeedbacks({ per_page: 100 }),
  })

  const feedbacks = feedbackData?.data || []

  return (
    <RequireAuth>
      <FeedbackProvider>
        <Header fixed>
          <Search />
          <div className='ms-auto flex items-center space-x-4'>
            <ThemeSwitch />
            <ConfigDrawer />
            <ProfileDropdown />
          </div>
        </Header>

        <Main className='flex flex-1 flex-col gap-4 sm:gap-6'>
          <div className='flex flex-wrap items-end justify-between gap-2'>
            <div>
              <h2 className='text-2xl font-bold tracking-tight'>反馈管理</h2>
              <p className='text-muted-foreground'>
                查看和处理用户反馈及调度异常
              </p>
            </div>
            <FeedbackPrimaryButtons />
          </div>
          <FeedbackTable data={feedbacks} />
        </Main>

        <FeedbackDialogs />
      </FeedbackProvider>
    </RequireAuth>
  )
}



