import { ConfigDrawer } from '@/components/config-drawer'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { Search } from '@/components/search'
import { DemandDialogs } from './components/demand-dialogs'
import { DemandPrimaryButtons } from './components/demand-primary-buttons'
import { DemandProvider } from './components/demand-provider'
import { DemandTable } from './components/demand-table'
import { RequireAuth } from '@/components/require-auth'
import { useQuery } from '@tanstack/react-query'
import { getDemands } from './service'

export function DemandManagement() {
  const { data: demandData } = useQuery({
    queryKey: ['demands'],
    queryFn: () => getDemands({ per_page: 100 }),
  })

  const demands = demandData?.data || []

  return (
    <RequireAuth>
      <DemandProvider>
        <Header fixed>
          <Search />
          <div className='ms-auto flex items-center space-x-4'>
            <ConfigDrawer />
          </div>
        </Header>

        <Main className='flex flex-1 flex-col gap-4 sm:gap-6'>
          <div className='flex flex-wrap items-end justify-between gap-2'>
            <div>
              <h2 className='text-2xl font-bold tracking-tight'>需求数据管理</h2>
              <p className='text-muted-foreground'>
                这里是您的需求数据列表
              </p>
            </div>
            <DemandPrimaryButtons />
          </div>
          <DemandTable data={demands} />
        </Main>

        <DemandDialogs />
      </DemandProvider>
    </RequireAuth>
  )
}
