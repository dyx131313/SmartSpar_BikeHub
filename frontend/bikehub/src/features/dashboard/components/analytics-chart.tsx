import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { type Task } from '@/features/task_management/data/schema'

interface AnalyticsChartProps {
  data: Task[]
}

export function AnalyticsChart({ data }: AnalyticsChartProps) {
  // Generate last 7 days
  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - i))
    return d
  })

  const chartData = last7Days.map((date) => {
    const dateStr = date.toISOString().split('T')[0] // YYYY-MM-DD
    const dayName = date.toLocaleDateString('en-US', { weekday: 'short' })

    const createdCount = data.filter((t) => t.created_at && t.created_at.startsWith(dateStr)).length
    // Assuming updated_at is the completion time for completed tasks
    const completedCount = data.filter(
      (t) => t.status === 'completed' && t.updated_at && t.updated_at.startsWith(dateStr)
    ).length

    return {
      name: dayName,
      created: createdCount,
      completed: completedCount,
    }
  })

  return (
    <ResponsiveContainer width='100%' height={300}>
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id='colorCreated' x1='0' y1='0' x2='0' y2='1'>
            <stop offset='5%' stopColor='#8884d8' stopOpacity={0.8} />
            <stop offset='95%' stopColor='#8884d8' stopOpacity={0} />
          </linearGradient>
          <linearGradient id='colorCompleted' x1='0' y1='0' x2='0' y2='1'>
            <stop offset='5%' stopColor='#82ca9d' stopOpacity={0.8} />
            <stop offset='95%' stopColor='#82ca9d' stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey='name'
          stroke='#888888'
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke='#888888'
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `${value}`}
        />
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <Tooltip />
        <Area
          type='monotone'
          dataKey='created'
          stroke='#8884d8'
          fillOpacity={1}
          fill='url(#colorCreated)'
          name='新创建'
        />
        <Area
          type='monotone'
          dataKey='completed'
          stroke='#82ca9d'
          fillOpacity={1}
          fill='url(#colorCompleted)'
          name='已完成'
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
