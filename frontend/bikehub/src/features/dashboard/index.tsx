import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ConfigDrawer } from '@/components/config-drawer'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { TopNav } from '@/components/layout/top-nav'
// import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
// import { ThemeSwitch } from '@/components/theme-switch'
import { Analytics } from './components/analytics'
// import { Overview } from './components/overview'
import { RecentSales } from './components/recent-sales'
import { AmapComponent } from './components/amap'
import { ListTodo, HelpCircle, Timer, CheckCircle } from 'lucide-react'
import { tasks } from '@/features/task_management/data/tasks'
import { stations } from '@/features/station_management/data/stations'
import { users } from '@/features/users/data/users'
import { status as userStatuses, roles as userRoles } from '@/features/users/data/data'

export function Dashboard() {
  // 基于模拟任务数据的实时统计
  const totalTasks = tasks.length
  let backlogTasks = 0
  let inProgressTasks = 0
  let completedTasks = 0
  for (const t of tasks) {
    switch (t.status) {
      case '积压':
        backlogTasks++
        break
      case '正在进行':
        inProgressTasks++
        break
      case '已完成':
        completedTasks++
        break
      default:
        break
    }
  }

  // 站点分析所需数据
  // 站点需求统计（临时：基于容量与ID派生一个稳定的“需求值”），取前五
  const demandTop5 = stations
    .map((s) => ({
      name: s.name,
      value: s.capacity * 2 + (parseInt(s.id, 10) % 50),
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 5)

  // 站点容量统计：从站点管理的数据中取容量前五
  const capacityTop5 = stations
    .slice()
    .sort((a, b) => b.capacity - a.capacity)
    .slice(0, 5)
    .map((s) => ({ name: s.name, value: s.capacity }))
  return (
    <>
      {/* ===== Top Heading ===== */}
      <Header>
        <TopNav links={topNav} />
        <div className='ms-auto flex items-center space-x-4'>
          <Search />
          {/* <ThemeSwitch /> */}
          <ConfigDrawer />
          {/* <ProfileDropdown /> */}
        </div>
      </Header>

      {/* ===== Main ===== */}
      <Main>
        <div className='mb-2 flex items-center justify-between space-y-2'>
          <h1 className='text-2xl font-bold tracking-tight'>Dashboard</h1>
          <div className='flex items-center space-x-2'>
            <Button>Download</Button>
          </div>
        </div>
        <Tabs
          orientation='vertical'
          defaultValue='overview'
          className='space-y-4'
        >
          <div className='w-full overflow-x-auto pb-2'>
            <TabsList>
              <TabsTrigger value='overview'>总览</TabsTrigger>
              <TabsTrigger value='analytics'>调度分析</TabsTrigger>
              <TabsTrigger value='reports'>站点分析</TabsTrigger>
              <TabsTrigger value='notifications'>用户分析</TabsTrigger>
            </TabsList>
          </div>
          <TabsContent value='overview' className='space-y-4'>
            <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
              <Card className='gap-3'>
                <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
                  <CardTitle className='text-lg font-medium'>
                    总调度数
                  </CardTitle>
                  <ListTodo className='text-muted-foreground h-5 w-5' />
                </CardHeader>
                <CardContent>
                  <div className='text-4xl font-extrabold md:text-5xl'>{totalTasks}</div>
                  <p className='text-muted-foreground text-xs'>
                    +20.1% from last day
                  </p>
                </CardContent>
              </Card>
              <Card className='gap-3'>
                <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
                  <CardTitle className='text-lg font-medium'>
                    积压调度数
                  </CardTitle>
                  <HelpCircle className='text-muted-foreground h-5 w-5' />
                </CardHeader>
                <CardContent>
                  <div className='text-4xl font-extrabold md:text-5xl'>{backlogTasks}</div>
                  <p className='text-muted-foreground text-xs'>
                    +180.1% from last day
                  </p>
                </CardContent>
              </Card>
              <Card className='gap-3'>
                <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
                  <CardTitle className='text-lg font-medium'>正在进行调度数</CardTitle>
                  <Timer className='text-muted-foreground h-5 w-5' />
                </CardHeader>
                <CardContent>
                  <div className='text-4xl font-extrabold md:text-5xl'>{inProgressTasks}</div>
                  <p className='text-muted-foreground text-xs'>
                    +19% from last day
                  </p>
                </CardContent>
              </Card>
              <Card className='gap-3'>
                <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
                  <CardTitle className='text-lg font-medium'>
                    已完成调度数
                  </CardTitle>
                  <CheckCircle className='text-muted-foreground h-5 w-5' />
                </CardHeader>
                <CardContent>
                  <div className='text-4xl font-extrabold md:text-5xl'>{completedTasks}</div>
                  <p className='text-muted-foreground text-xs'>
                    +201 since last day
                  </p>
                </CardContent>
              </Card>
            </div>
            <div className='grid grid-cols-1 gap-4 lg:grid-cols-7'>
              <Card className='col-span-1 lg:col-span-4'>
                <CardContent className='pt-6'>
                  <Tabs defaultValue='heatmap' className='space-y-4'>
                    <div className='w-full overflow-x-auto pb-2'>
                      <TabsList>
                        <TabsTrigger value='heatmap'>热力图</TabsTrigger>
                        <TabsTrigger value='markers'>图钉图</TabsTrigger>
                      </TabsList>
                    </div>
                    <TabsContent value='heatmap' className='ps-2'>
                      <AmapComponent mode='heatmap' />
                    </TabsContent>
                    <TabsContent value='markers' className='ps-2'>
                      <AmapComponent mode='markers' />
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
              <Card className='col-span-1 lg:col-span-3'>
                <CardHeader>
                  <CardTitle>站点需求排行</CardTitle>
                  <CardDescription>
                    按照调度需求量排序的站点。
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <RecentSales />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          <TabsContent value='analytics' className='space-y-4'>
            <Analytics />
          </TabsContent>
          <TabsContent value='reports' className='space-y-4'>
            <div className='grid gap-4'>
              <Card>
                <CardHeader>
                  <CardTitle>站点地图</CardTitle>
                  <CardDescription>支持热力图与图钉图切换。</CardDescription>
                </CardHeader>
                <CardContent className='pt-6'>
                  <Tabs defaultValue='heatmap' className='space-y-4'>
                    <div className='w-full overflow-x-auto pb-2'>
                      <TabsList>
                        <TabsTrigger value='heatmap'>热力图</TabsTrigger>
                        <TabsTrigger value='markers'>图钉图</TabsTrigger>
                      </TabsList>
                    </div>
                    <TabsContent value='heatmap' className='ps-2'>
                      <AmapComponent mode='heatmap' height={520} />
                    </TabsContent>
                    <TabsContent value='markers' className='ps-2'>
                      <AmapComponent mode='markers' height={520} />
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>

              <div className='grid grid-cols-1 gap-4 lg:grid-cols-7'>
                <Card className='col-span-1 lg:col-span-4'>
                  <CardHeader>
                    <CardTitle>站点需求统计（Top 5）</CardTitle>
                    <CardDescription>临时数据：根据容量与ID派生的需求值。</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <SimpleBarList
                      items={demandTop5}
                      barClass='bg-primary'
                      valueFormatter={(n) => `${n}`}
                    />
                  </CardContent>
                </Card>
                <Card className='col-span-1 lg:col-span-3'>
                  <CardHeader>
                    <CardTitle>站点容量统计（Top 5）</CardTitle>
                    <CardDescription>来自站点管理的容量数据。</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <SimpleBarList
                      items={capacityTop5}
                      barClass='bg-muted-foreground'
                      valueFormatter={(n) => `${n}`}
                    />
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
          <TabsContent value='notifications' className='space-y-4'>
            <div className='grid grid-cols-1 gap-4 lg:grid-cols-7'>
              <Card className='col-span-1 lg:col-span-4'>
                <CardHeader>
                  <CardTitle>用户状态统计</CardTitle>
                  <CardDescription>来自用户管理面板的实时状态分布。</CardDescription>
                </CardHeader>
                <CardContent>
                  <SimpleBarList
                    items={userStatuses.map((s) => ({
                      name: s.label,
                      value: users.filter((u) => u.status === s.label).length,
                    }))}
                    barClass='bg-primary'
                    valueFormatter={(n) => `${n}`}
                  />
                </CardContent>
              </Card>
              <Card className='col-span-1 lg:col-span-3'>
                <CardHeader>
                  <CardTitle>用户角色统计</CardTitle>
                  <CardDescription>来自用户管理面板的角色分布。</CardDescription>
                </CardHeader>
                <CardContent>
                  <SimpleBarList
                    items={userRoles.map((r) => ({
                      name: r.label,
                      value: users.filter((u) => u.role === r.label).length,
                    }))}
                    barClass='bg-muted-foreground'
                    valueFormatter={(n) => `${n}`}
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </Main>
    </>
  )
}

const topNav = [
  {
    title: 'Overview',
    href: 'dashboard/overview',
    isActive: true,
    disabled: false,
  },
  {
    title: 'Customers',
    href: 'dashboard/customers',
    isActive: false,
    disabled: true,
  },
  {
    title: 'Products',
    href: 'dashboard/products',
    isActive: false,
    disabled: true,
  },
  {
    title: 'Settings',
    href: 'dashboard/settings',
    isActive: false,
    disabled: true,
  },
]

function SimpleBarList({
  items,
  valueFormatter,
  barClass,
}: {
  items: { name: string; value: number }[]
  valueFormatter: (n: number) => string
  barClass: string
}) {
  const max = Math.max(...items.map((i) => i.value), 1)
  return (
    <ul className='space-y-3'>
      {items.map((i) => {
        const width = `${Math.round((i.value / max) * 100)}%`
        return (
          <li key={i.name} className='flex items-center justify-between gap-3'>
            <div className='min-w-0 flex-1'>
              <div className='text-muted-foreground mb-1 truncate text-xs'>
                {i.name}
              </div>
              <div className='bg-muted h-2.5 w-full rounded-full'>
                <div
                  className={`h-2.5 rounded-full ${barClass}`}
                  style={{ width }}
                />
              </div>
            </div>
            <div className='ps-2 text-xs font-medium tabular-nums'>
              {valueFormatter(i.value)}
            </div>
          </li>
        )
      })}
    </ul>
  )
}
