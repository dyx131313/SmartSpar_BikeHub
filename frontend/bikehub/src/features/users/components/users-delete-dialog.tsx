'use client'

import { useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { type User } from '../data/schema'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteUser } from '../service'
import { toast } from 'sonner'

type UserDeleteDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentRow: User
}

export function UsersDeleteDialog({
  open,
  onOpenChange,
  currentRow,
}: UserDeleteDialogProps) {
  const [value, setValue] = useState('')
  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast.success('用户删除成功')
      onOpenChange(false)
    },
    onError: (error: any) => {
      toast.error('删除失败', { description: error.message })
    },
  })

  const handleDelete = () => {
    if (value.trim() !== currentRow.username) return

    deleteMutation.mutate(currentRow.id)
  }

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      handleConfirm={handleDelete}
      disabled={value.trim() !== currentRow.username}
      title={
        <span className='text-destructive'>
          <AlertTriangle
            className='stroke-destructive me-1 inline-block'
            size={18}
          />{' '}
          删除用户
        </span>
      }
      desc={
        <div className='space-y-4'>
          <p className='mb-2'>
            您确定要删除{' '}
            <span className='font-bold'>{currentRow.username}</span>吗？
            <br />
            此操作将永久删除具有{' '}
            <span className='font-bold'>
              {currentRow.role.toUpperCase()}
            </span>{' '}
            身份的用户。这是不可逆的操作。
          </p>

          <Label className='my-2'>
            用户名确认：
            <Input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder='请输入用户名以确认删除。'
            />
          </Label>

          <Alert variant='destructive'>
            <AlertTitle>警告！</AlertTitle>
            <AlertDescription>
              请注意，此操作无法撤销。
            </AlertDescription>
          </Alert>
        </div>
      }
      confirmText='删除用户'
      destructive
    />
  )
}
