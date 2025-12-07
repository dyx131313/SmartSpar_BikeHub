import { DotsHorizontalIcon } from '@radix-ui/react-icons'
import { type Row } from '@tanstack/react-table'
import { Trash2, Map, CheckCircle, AlertTriangle, Edit } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { taskSchema } from '../data/schema'
import { useTasks } from './tasks-provider'
import { useAuthStore } from '@/stores/auth-store'

type DataTableRowActionsProps<TData> = {
  row: Row<TData>
}

export function DataTableRowActions<TData>({
  row,
}: DataTableRowActionsProps<TData>) {
  const task = taskSchema.parse(row.original)
  const { setOpen, setCurrentRow } = useTasks()
  const { user } = useAuthStore((state) => state.auth)
  
  const isDispatcher = user?.role === 'dispatcher'
  const isAdmin = user?.role === 'admin'
  const isOperator = user?.role === 'operator' // 假设有 operator 角色，或者 dispatcher 兼任

  // 如果当前任务状态不是 completed，才显示完成按钮
  const isPendingOrProgress = task.status !== 'completed' && task.status !== 'cancelled'

  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <Button
          variant='ghost'
          className='data-[state=open]:bg-muted flex h-8 w-8 p-0'
        >
          <DotsHorizontalIcon className='h-4 w-4' />
          <span className='sr-only'>Open menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align='end' className='w-[160px]'>
        
        {/* 调度员/运维员 操作 */}
        {(isDispatcher || isOperator) && (
          <>
            <DropdownMenuItem
              onClick={() => {
                setCurrentRow(task)
                setOpen('view-route')
              }}
            >
              查看路线
              <DropdownMenuShortcut>
                <Map size={16} />
              </DropdownMenuShortcut>
            </DropdownMenuItem>

            {isPendingOrProgress && (
              <DropdownMenuItem
                onClick={() => {
                  setCurrentRow(task)
                  setOpen('complete')
                }}
              >
                完成任务
                <DropdownMenuShortcut>
                  <CheckCircle size={16} />
                </DropdownMenuShortcut>
              </DropdownMenuItem>
            )}

            <DropdownMenuItem
              onClick={() => {
                setCurrentRow(task)
                setOpen('report')
              }}
            >
              报告异常
              <DropdownMenuShortcut>
                <AlertTriangle size={16} />
              </DropdownMenuShortcut>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}

        {/* 管理员/调度员(仅创建者) 编辑删除 */}
        {(isAdmin) && (
          <>
            <DropdownMenuItem
              onClick={() => {
                setCurrentRow(task)
                setOpen('update')
              }}
            >
              编辑
              <DropdownMenuShortcut>
                <Edit size={16} />
              </DropdownMenuShortcut>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => {
                setCurrentRow(task)
                setOpen('delete')
              }}
            >
              删除
              <DropdownMenuShortcut>
                <Trash2 size={16} />
              </DropdownMenuShortcut>
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
