import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { AnalyticsChart } from './analytics-chart'
import { ListTodo, HelpCircle, Timer, CheckCircle, Circle } from 'lucide-react'
import { priorities, statuses } from '@/features/task_management/data/data'
import { Task } from '@/features/task_management/data/schema'

interface AnalyticsProps {
  data: Task[]
}

export function Analytics({ data: tasks }: AnalyticsProps) {
  // 统计调度任务实时数据
  const totalTasks = tasks.length
  let todoTasks = 0
  let inProgressTasks = 0
  let completedTasks = 0
  for (const t of tasks) {
    switch (t.status) {
      case 'pending':
        todoTasks++
        break
      case 'in_progress':
        inProgressTasks++
        break
      case 'completed':
        completedTasks++
        break
      default:
        break
    }
  }
  return (
    <div className='space-y-4'>
      <Card>
        <CardHeader>
          <CardTitle>调度数曲线</CardTitle>
          <CardDescription>本周的各项调度数统计。</CardDescription>
        </CardHeader>
        <CardContent className='px-6'>
          <AnalyticsChart data={tasks} />
        </CardContent>
      </Card>
      <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
        <Card className='gap-3'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
            <CardTitle className='text-sm font-medium'>总调度数</CardTitle>
            <ListTodo className='text-muted-foreground h-5 w-5' />
          </CardHeader>
          <CardContent>
            <div className='text-4xl font-extrabold md:text-5xl'>{totalTasks}</div>
            {/* <p className='text-muted-foreground text-xs'>+20.1% from last day</p> */}
          </CardContent>
        </Card>
        <Card className='gap-3'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
            <CardTitle className='text-sm font-medium'>待办调度数</CardTitle>
            <Circle className='text-muted-foreground h-5 w-5' />
          </CardHeader>
          <CardContent>
            <div className='text-4xl font-extrabold md:text-5xl'>{todoTasks}</div>
            {/* <p className='text-muted-foreground text-xs'>+180.1% from last day</p> */}
          </CardContent>
        </Card>
        <Card className='gap-3'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
            <CardTitle className='text-sm font-medium'>正在进行调度数</CardTitle>
            <Timer className='text-muted-foreground h-5 w-5' />
          </CardHeader>
          <CardContent>
            <div className='text-4xl font-extrabold md:text-5xl'>{inProgressTasks}</div>
            {/* <p className='text-muted-foreground text-xs'>+19% from last day</p> */}
          </CardContent>
        </Card>
        <Card className='gap-3'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-1'>
            <CardTitle className='text-sm font-medium'>已完成调度数</CardTitle>
            <CheckCircle className='text-muted-foreground h-5 w-5' />
          </CardHeader>
          <CardContent>
            <div className='text-4xl font-extrabold md:text-5xl'>{completedTasks}</div>
            {/* <p className='text-muted-foreground text-xs'>+201 since last day</p> */}
          </CardContent>
        </Card>
      </div>
      <div className='grid grid-cols-1 gap-4 lg:grid-cols-7'>
        <Card className='col-span-1 lg:col-span-4'>
          <CardHeader>
            <CardTitle>状态统计</CardTitle>
            <CardDescription>按调度状态统计任务数量</CardDescription>
          </CardHeader>
          <CardContent>
            <SimpleBarList
              items={statuses.map((s) => ({
                name: s.label,
                value: tasks.filter((t) => t.status === s.value).length,
              }))}
              barClass='bg-primary'
              valueFormatter={(n) => `${n}`}
            />
          </CardContent>
        </Card>
        <Card className='col-span-1 lg:col-span-3'>
          <CardHeader>
            <CardTitle>优先级统计</CardTitle>
            <CardDescription>按优先级统计任务数量</CardDescription>
          </CardHeader>
          <CardContent>
            <SimpleBarList
              items={priorities.map((p) => ({
                name: p.label,
                value: tasks.filter((t) => t.priority === p.value).length,
              }))}
              barClass='bg-muted-foreground'
              valueFormatter={(n) => `${n}`}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

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
