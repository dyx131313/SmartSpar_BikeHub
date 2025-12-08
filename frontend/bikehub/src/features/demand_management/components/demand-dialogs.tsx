import { ConfirmDialog } from '@/components/confirm-dialog'
import { DemandImportDialog } from './demand-import-dialog'
import { DemandMutateDrawer } from './demand-mutate-drawer'
import { useDemand } from './demand-provider'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteDemand } from '../service'
import { toast } from 'sonner'

export function DemandDialogs() {
  const { open, setOpen, currentRow, setCurrentRow } = useDemand()
  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: deleteDemand,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['demands'] })
      toast.success('需求数据已删除', {
        description: `需求数据 ${currentRow?.id} 已成功删除。`,
      })
      setOpen(null)
      setTimeout(() => {
        setCurrentRow(null)
      }, 500)
    },
    onError: (error: any) => {
      toast.error('删除失败', {
        description: error.message || '无法删除该需求数据。',
      })
    }
  })

  return (
    <>
      <DemandMutateDrawer
        key='demand-create'
        open={open === 'create'}
        onOpenChange={() => setOpen('create')}
      />

      <DemandImportDialog
        key='demand-import'
        open={open === 'import'}
        onOpenChange={() => setOpen('import')}
      />

      {currentRow && (
        <>
          <DemandMutateDrawer
            key={`demand-update-${currentRow.id}`}
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
            key='demand-delete'
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
            title={`删除需求数据: ${currentRow.id} ?`}
            desc={
              <>
                你确定你要删除ID为{' '}
                <strong>{currentRow.id}</strong> 的需求数据吗？ <br />
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
