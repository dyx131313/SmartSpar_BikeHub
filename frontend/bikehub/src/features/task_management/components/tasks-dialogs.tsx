import { ConfirmDialog } from '@/components/confirm-dialog'
import { TasksImportDialog } from './tasks-import-dialog'
import { TasksMutateDrawer } from './tasks-mutate-drawer'
import { TasksRouteDialog } from './tasks-route-dialog'
import { TasksReportDialog } from './tasks-report-dialog'
import { useTasks } from './tasks-provider'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteTask, updateTask } from '../service'
import { toast } from 'sonner'

export function TasksDialogs() {
  const { open, setOpen, currentRow, setCurrentRow } = useTasks()
  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('任务已删除', {
        description: `任务 ${currentRow?.id} 已成功删除。`,
      })
      setOpen(null)
      setTimeout(() => {
        setCurrentRow(null)
      }, 500)
    },
    onError: (error: any) => {
      toast.error('删除失败', {
        description: error.message || '无法删除该任务。',
      })
    }
  })

  const completeMutation = useMutation({
    mutationFn: (id: number) => updateTask(id, { status: 'completed' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('任务已完成', {
        description: `任务 ${currentRow?.id} 已标记为完成。`,
      })
      setOpen(null)
      setTimeout(() => {
        setCurrentRow(null)
      }, 500)
    },
    onError: (error: any) => {
      toast.error('操作失败', {
        description: error.message || '无法完成该任务。',
      })
    }
  })

  return (
    <>
      <TasksMutateDrawer
        key='task-create'
        open={open === 'create'}
        onOpenChange={() => setOpen('create')}
      />

      <TasksImportDialog
        key='tasks-import'
        open={open === 'import'}
        onOpenChange={() => setOpen('import')}
      />

      <TasksRouteDialog key='task-route' />
      <TasksReportDialog key='task-report' />

      {currentRow && (
        <>
          <TasksMutateDrawer
            key={`task-update-${currentRow.id}`}
            open={open === 'update'}
            onOpenChange={() => {
              setOpen('update')
              setTimeout(() => {
                setCurrentRow(null)
              }, 500)
            }}
            currentRow={currentRow}
          />

          <ConfirmDialog
            key='task-delete'
            destructive
            open={open === 'delete'}
            onOpenChange={() => {
              setOpen('delete')
              setTimeout(() => {
                setCurrentRow(null)
              }, 500)
            }}
            handleConfirm={() => {
              deleteMutation.mutate(currentRow.id)
            }}
            className='max-w-md'
            title={`删除任务: ${currentRow.id} ?`}
            desc={
              <>
                你确定你要删除ID为{' '}
                <strong>{currentRow.id}</strong> 的任务吗？ <br />
                这个操作无法撤销。
              </>
            }
            confirmText='删除'
          />

          <ConfirmDialog
            key='task-complete'
            open={open === 'complete'}
            onOpenChange={() => {
              setOpen('complete')
              setTimeout(() => {
                setCurrentRow(null)
              }, 500)
            }}
            handleConfirm={() => {
              completeMutation.mutate(currentRow.id)
            }}
            className='max-w-md'
            title={`完成任务: ${currentRow.task_name} ?`}
            desc={
              <>
                你确定要将任务 <strong>{currentRow.task_name}</strong> 标记为已完成吗？
              </>
            }
            confirmText='确认完成'
          />
        </>
      )}
    </>
  )
}
