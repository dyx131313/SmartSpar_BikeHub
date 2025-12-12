import { ConfigDrawer } from '@/components/config-drawer'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { Search } from '@/components/search'
import { DemandDialogs } from './components/demand-dialogs'
import { DemandPrimaryButtons } from './components/demand-primary-buttons'
import { DemandProvider } from './components/demand-provider'
import { DemandTable } from './components/demand-table'
import { RequireRole } from '@/components/require-role'
import { useQuery } from '@tanstack/react-query'
import { getDemands } from './service'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PredictedDemandView } from './components/predicted-demand-view'

export function DemandManagement() {
  const { data: demandData } = useQuery({
    queryKey: ['demands'],
    queryFn: () => getDemands({ per_page: 100 }),
  })

  const demands = demandData?.data || []

  return (
    <RequireRole roles={["admin", "dispatcher"]}>
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
          </div>

          <Tabs defaultValue="realtime" className="space-y-4">
            <TabsList>
              <TabsTrigger value="realtime">实时需求</TabsTrigger>
              <TabsTrigger value="predicted">预测需求</TabsTrigger>
            </TabsList>

            <TabsContent value="realtime" className="space-y-4">
              <div className="flex justify-end">
                <DemandPrimaryButtons />
              </div>
              <DemandTable data={demands} />
            </TabsContent>

            <TabsContent value="predicted" className="space-y-4">
              <PredictedDemandView />
            </TabsContent>
          </Tabs>

        </Main>

        <DemandDialogs />
      </DemandProvider>
    </RequireRole>
  )
}
