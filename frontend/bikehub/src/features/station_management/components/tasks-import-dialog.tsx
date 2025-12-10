import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
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
import { importStations } from '../service'

const formSchema = z.object({
  file: z
    .instanceof(FileList)
    .refine((files) => files.length > 0, {
      message: 'Please upload a file',
    })
    .refine(
      (files) => ['application/json', 'text/csv'].includes(files?.[0]?.type) || files?.[0]?.name.endsWith('.json'),
      'Please upload json or csv format.'
    ),
})

type TaskImportDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function TasksImportDialog({
  open,
  onOpenChange,
}: TaskImportDialogProps) {
  const queryClient = useQueryClient()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { file: undefined },
  })

  const fileRef = form.register('file')

  const { mutate: importFile, isPending } = useMutation({
    mutationFn: importStations,
    onSuccess: () => {
      toast.success('站点数据导入成功')
      queryClient.invalidateQueries({ queryKey: ['stations'] })
      onOpenChange(false)
    },
    onError: (error: any) => {
      toast.error('导入失败: ' + (error.message || '未知错误'))
    },
  })

  const onSubmit = () => {
    const file = form.getValues('file')

    if (file && file[0]) {
      importFile(file[0])
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
          <DialogTitle>导入站点数据</DialogTitle>
          <DialogDescription>
            {/* Import tasks quickly from a CSV file. */}
            从 JSON 文件快速导入站点数据。
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form id='task-import-form' onSubmit={form.handleSubmit(onSubmit)}>
            <FormField
              control={form.control}
              name='file'
              render={() => (
                <FormItem className='my-2'>
                  <FormLabel>文件</FormLabel>
                  <FormControl>
                    <Input type='file' {...fileRef} className='h-8 py-0' accept=".json,.csv" />
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
          <Button type='submit' form='task-import-form' disabled={isPending}>
            {isPending ? '导入中...' : '导入'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
