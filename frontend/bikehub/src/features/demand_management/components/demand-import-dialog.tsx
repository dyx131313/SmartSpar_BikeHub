import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { importDemands } from '../service'
import { toast } from 'sonner'

const formSchema = z.object({
  file: z
    .instanceof(FileList)
    .refine((files) => files.length > 0, {
      message: 'Please upload a file',
    })
    .refine(
      (files) => ['application/json'].includes(files?.[0]?.type),
      'Please upload json format.'
    ),
})

type DemandImportDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function DemandImportDialog({
  open,
  onOpenChange,
}: DemandImportDialogProps) {
  const queryClient = useQueryClient()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { file: undefined },
  })

  const fileRef = form.register('file')

  const importMutation = useMutation({
    mutationFn: (file: File) => importDemands(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['demands'] })
      toast.success('导入成功', {
        description: '需求数据已成功导入。',
      })
      onOpenChange(false)
    },
    onError: (error: any) => {
      toast.error('导入失败', {
        description: error.message || '无法导入数据。',
      })
    }
  })

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    const file = data.file[0]
    if (file) {
      importMutation.mutate(file)
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(val) => {
        onOpenChange(val)
        form.reset()
      }}
    >
      <DialogContent className='gap-2 sm:max-w-sm'>
        <DialogHeader className='text-start'>
          <DialogTitle>导入需求数据</DialogTitle>
          <DialogDescription>
            快速从JSON文件导入需求数据。
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form id='demand-import-form' onSubmit={form.handleSubmit(onSubmit)}>
            <FormField
              control={form.control}
              name='file'
              render={() => (
                <FormItem className='my-2'>
                  <FormLabel>文件</FormLabel>
                  <FormControl>
                    <Input type='file' accept='.json' {...fileRef} className='h-8 py-0' />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </form>
        </Form>
        <DialogFooter className='gap-2'>
          <DialogClose asChild>
            <Button variant='outline'>取消</Button>
          </DialogClose>
          <Button type='submit' form='demand-import-form' disabled={importMutation.isPending}>
            {importMutation.isPending ? '导入中...' : '导入'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
