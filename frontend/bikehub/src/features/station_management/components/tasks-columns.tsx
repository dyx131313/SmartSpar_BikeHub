import { type ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { DataTableColumnHeader } from '@/components/data-table'
import { labels, priorities, statuses } from '../data/data'
import { type Station } from '../data/schema'
import { DataTableRowActions } from './data-table-row-actions'

export const tasksColumns: ColumnDef<Station>[] = [
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
      <DataTableColumnHeader column={column} title='站点ID' />
    ),
    cell: ({ row }) => <div className='w-[80px]'>{row.getValue('id')}</div>,
    enableSorting: false,
    enableHiding: false,
  },
  // {
  //   accessorKey: 'title',
  //   header: ({ column }) => (
  //     <DataTableColumnHeader column={column} title='Title' />
  //   ),
  //   meta: { className: 'ps-1', tdClassName: 'ps-4' },
  //   cell: ({ row }) => {
  //     const label = labels.find((label) => label.value === row.original.label)

  //     return (
  //       <div className='flex space-x-2'>
  //         {label && <Badge variant='outline'>{label.label}</Badge>}
  //         <span className='max-w-32 truncate font-medium sm:max-w-72 md:max-w-[31rem]'>
  //           {row.getValue('title')}
  //         </span>
  //       </div>
  //     )
  //   },
  // },
  {
    accessorKey: 'name',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='站点名称' />
    ),
    meta: { title: '站点名称', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => (
      <div className='max-w-40 truncate text-sm text-gray-700'>
        {row.getValue('name') ?? '—'}
      </div>
    ),
  },
  {
    accessorKey: 'station_type',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='站点类型' />
    ),
    meta: { title: '站点类型', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => (
      <div className='max-w-40 truncate text-sm text-gray-700'>
        {row.getValue('station_type') ?? '—'}
      </div>
    ),
  },
  {
    accessorKey: 'latitude',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='纬度' />
    ),
    meta: { title:'纬度', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => (
      <div className='max-w-40 truncate text-sm text-gray-700'>
        {row.getValue('latitude') ?? '—'}
      </div>
    ),
  },
  {
    accessorKey: 'longitude',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='经度' />
    ),
    meta: { title:'经度', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => (
      <div className='max-w-40 truncate text-sm text-gray-700'>
        {row.getValue('longitude') ?? '—'}
      </div>
    ),
  },
  {
    accessorKey: 'capacity',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='容量' />
    ),
    meta: {title:'容量', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => (
      <div className='max-w-40 truncate text-sm text-gray-700'>
        {row.getValue('capacity') ?? '—'}
      </div>
    ),
  },
  {
    accessorKey: 'description',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='描述' />
    ),
    meta: { title:'描述',className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => (
      <div className='max-w-40 truncate text-sm text-gray-700'>
        {row.getValue('description') ?? '—'}
      </div>
    ),
  },
  // {
  //   accessorKey: 'status',
  //   header: ({ column }) => (
  //     <DataTableColumnHeader column={column} title='Status' />
  //   ),
  //   meta: { className: 'ps-1', tdClassName: 'ps-4' },
  //   cell: ({ row }) => {
  //     const status = statuses.find(
  //       (status) => status.value === row.getValue('status')
  //     )

  //     if (!status) {
  //       return null
  //     }

  //     return (
  //       <div className='flex w-[100px] items-center gap-2'>
  //         {status.icon && (
  //           <status.icon className='text-muted-foreground size-4' />
  //         )}
  //         <span>{status.label}</span>
  //       </div>
  //     )
  //   },
  //   filterFn: (row, id, value) => {
  //     return value.includes(row.getValue(id))
  //   },
  // },
  // {
  //   accessorKey: 'priority',
  //   header: ({ column }) => (
  //     <DataTableColumnHeader column={column} title='Priority' />
  //   ),
  //   meta: { className: 'ps-1', tdClassName: 'ps-3' },
  //   cell: ({ row }) => {
  //     const priority = priorities.find(
  //       (priority) => priority.value === row.getValue('priority')
  //     )

  //     if (!priority) {
  //       return null
  //     }

  //     return (
  //       <div className='flex items-center gap-2'>
  //         {priority.icon && (
  //           <priority.icon className='text-muted-foreground size-4' />
  //         )}
  //         <span>{priority.label}</span>
  //       </div>
  //     )
  //   },
  //   filterFn: (row, id, value) => {
  //     return value.includes(row.getValue(id))
  //   },
  // },
  {
    id: 'actions',
    cell: ({ row }) => <DataTableRowActions row={row} />,
  },
]
