import { ConfirmDialog } from '@/components/confirm-dialog'
import { TasksImportDialog } from './tasks-import-dialog'
import { TasksMutateDrawer } from './tasks-mutate-drawer'
import { useTasks } from './tasks-provider'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteTask } from '../service'
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
        </>
      )}
    </>
  )
}