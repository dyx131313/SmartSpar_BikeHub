'use client'

import { useState } from 'react'
import { type Table } from '@tanstack/react-table'
import { AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteTask } from '../service'

type TaskMultiDeleteDialogProps<TData> = {
  open: boolean
  onOpenChange: (open: boolean) => void
  table: Table<TData>
}

const CONFIRM_WORD = 'DELETE'

export function TasksMultiDeleteDialog<TData>({
  open,
  onOpenChange,
  table,
}: TaskMultiDeleteDialogProps<TData>) {
  const [value, setValue] = useState('')
  const queryClient = useQueryClient()
  const selectedRows = table.getFilteredSelectedRowModel().rows

  // 批量删除逻辑：循环调用删除接口
  const batchDeleteMutation = useMutation({
    mutationFn: async (rows: typeof selectedRows) => {
      const promises = rows.map((row) => deleteTask((row.original as any).id))
      return Promise.all(promises)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      table.resetRowSelection()
      toast.success('批量删除成功', {
        description: `已成功删除 ${selectedRows.length} 个任务。`,
      })
      onOpenChange(false)
    },
    onError: (error: any) => {
      toast.error('批量删除失败', {
        description: error.message || '部分任务可能未被删除。',
      })
      onOpenChange(false)
    }
  })

  const handleDelete = () => {
    if (value.trim() !== CONFIRM_WORD) {
      toast.error(`请输入 "${CONFIRM_WORD}" 来确认。`)
      return
    }

    batchDeleteMutation.mutate(selectedRows)
  }

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      handleConfirm={handleDelete}
      disabled={value.trim() !== CONFIRM_WORD || batchDeleteMutation.isPending}
      title={
        <span className='text-destructive'>
          <AlertTriangle
            className='stroke-destructive me-1 inline-block'
            size={18}
          />{' '}
          删除 {selectedRows.length}{' '}
          {selectedRows.length > 1 ? '个任务' : '个任务'}
        </span>
      }
      desc={
        <div className='space-y-4'>
          <p className='mb-2'>
            你确定你要删除选中的任务吗？ <br />
            这个操作无法撤销。
          </p>

          <Label className='my-4 flex flex-col items-start gap-1.5'>
            <span className=''>通过输入 "{CONFIRM_WORD}" 来确认:</span>
            <Input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={`输入 "${CONFIRM_WORD}" 来确认.`}
            />
          </Label>

          <Alert variant='destructive'>
            <AlertTitle>警告！</AlertTitle>
            <AlertDescription>
              请注意，这个操作无法撤销。
            </AlertDescription>
          </Alert>
        </div>
      }
      confirmText={batchDeleteMutation.isPending ? '删除中...' : '删除'}
      destructive
    />
  )
}