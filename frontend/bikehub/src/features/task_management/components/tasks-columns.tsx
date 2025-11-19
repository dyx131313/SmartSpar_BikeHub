import { type ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { DataTableColumnHeader } from '@/components/data-table'
import { labels, priorities, statuses } from '../data/data'
import { type Task } from '../data/schema'
import { DataTableRowActions } from './data-table-row-actions'

export const tasksColumns: ColumnDef<Task>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && 'indeterminate')
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label='Select all'
        className='translate-y-[2px]'
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label='Select row'
        className='translate-y-[2px]'
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'id',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='调度任务ID' />
    ),
    meta: { title: '调度任务ID', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[80px]'>{row.getValue('id')}</div>,
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'task_name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='任务名称' />
    ),
    meta: { title: '任务名称', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[150px] truncate'>{row.getValue('task_name')}</div>,
  },
  {
    accessorKey: 'from_station_id',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='起始站点ID' />
    ),
    meta: { title: '起始站点ID', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[120px]'>{row.getValue('from_station_id')}</div>,
    // enableSorting: false,
    // enableHiding: false,
  },
  {
    accessorKey: 'to_station_id',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='终点站点ID' />
    ),
    meta: { title: '终点站点ID', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[120px]'>{row.getValue('to_station_id')}</div>,
    // enableSorting: false,
    // enableHiding: false,
  },
  {
    accessorKey: 'bike_count',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='车辆数量' />
    ),
    meta: { title: '车辆数量', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[100px]'>{row.getValue('bike_count')}</div>,
    // enableSorting: false,
    // enableHiding: false,
  },
  {
    accessorKey: 'status',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='状态' />
    ),
    meta: { title: '状态', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => {
      const status = statuses.find(
        (status) => status.value === row.getValue('status')
      )

      if (!status) {
        return null
      }

      return (
        <div className='flex w-[100px] items-center gap-2'>
          {status.icon && (
            <status.icon className='text-muted-foreground size-4' />
          )}
          <span>{status.label}</span>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: 'priority',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='优先级' />
    ),
    meta: { title: '优先级', className: 'ps-1', tdClassName: 'ps-3' },
    cell: ({ row }) => {
      const priority = priorities.find(
        (priority) => priority.value === row.getValue('priority')
      )

      if (!priority) {
        return null
      }

      return (
        <div className='flex items-center gap-2'>
          {priority.icon && (
            <priority.icon className='text-muted-foreground size-4' />
          )}
          <span>{priority.label}</span>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => <DataTableRowActions row={row} />,
  },
]
