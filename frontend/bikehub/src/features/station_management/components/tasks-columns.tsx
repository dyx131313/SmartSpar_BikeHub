import { type ColumnDef } from '@tanstack/react-table'
import { Checkbox } from '@/components/ui/checkbox'
import { DataTableColumnHeader } from '@/components/data-table'
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
    meta: { title: '纬度', className: 'ps-1', tdClassName: 'ps-4' },
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
    meta: { title: '经度', className: 'ps-1', tdClassName: 'ps-4' },
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
    meta: { title: '容量', className: 'ps-1', tdClassName: 'ps-4' },
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
    meta: { title: '描述', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => (
      <div className='max-w-40 truncate text-sm text-gray-700'>
        {row.getValue('description') ?? '—'}
      </div>
    ),
  },
  {
    id: 'actions',
    cell: ({ row }) => <DataTableRowActions row={row} />,
  },
]
