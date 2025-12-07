import { type ColumnDef } from '@tanstack/react-table'
import { Checkbox } from '@/components/ui/checkbox'
import { DataTableColumnHeader } from '@/components/data-table'
import { stationTypes, weatherTypes } from '../data/data'
import { type Demand } from '../data/schema'
import { DemandRowActions } from './demand-row-actions'

export const demandColumns: ColumnDef<Demand>[] = [
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
      <DataTableColumnHeader column={column} title='ID' />
    ),
    meta: { title: 'ID', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[50px]'>{row.getValue('id')}</div>,
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'timestamp',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='时间' />
    ),
    meta: { title: '时间', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[150px]'>{new Date(row.getValue('timestamp')).toLocaleString()}</div>,
  },
  {
    accessorKey: 'station_id',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='站点ID' />
    ),
    meta: { title: '站点ID', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[80px]'>{row.getValue('station_id')}</div>,
  },
  {
    accessorKey: 'station_type',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='站点类型' />
    ),
    meta: { title: '站点类型', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => {
      const type = stationTypes.find(
        (t) => t.value === row.getValue('station_type')
      )

      if (!type) {
        return <span>{row.getValue('station_type')}</span>
      }

      return (
        <div className='flex w-[100px] items-center gap-2'>
          {type.icon && (
            <type.icon className='text-muted-foreground size-4' />
          )}
          <span>{type.label}</span>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: 'weather',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='天气' />
    ),
    meta: { title: '天气', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => {
      const weather = weatherTypes.find(
        (w) => w.value === row.getValue('weather')
      )

      if (!weather) {
        return <span>{row.getValue('weather')}</span>
      }

      return (
        <div className='flex items-center gap-2'>
          {weather.icon && (
            <weather.icon className='text-muted-foreground size-4' />
          )}
          <span>{weather.label}</span>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: 'temp',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='温度(°C)' />
    ),
    meta: { title: '温度', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[80px]'>{row.getValue('temp')}</div>,
  },
  {
    accessorKey: 'demand',
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title='需求量' />
    ),
    meta: { title: '需求量', className: 'ps-1', tdClassName: 'ps-4' },
    cell: ({ row }) => <div className='w-[80px]'>{row.getValue('demand')}</div>,
  },
  {
    id: 'actions',
    cell: ({ row }) => <DemandRowActions row={row} />,
  },
]
