import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { type CreateFeedbackData, createFeedback } from '@/features/feedback/api'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useTasks } from './tasks-provider'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { useEffect } from 'react'

const formSchema = z.object({
  title: z.string().min(1, '请输入标题'),
  content: z.string().min(1, '请输入内容'),
})

export function TasksReportDialog() {
  const { open, setOpen, currentRow } = useTasks()
  const isOpen = open === 'report'

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: '',
      content: '',
    },
  })

  useEffect(() => {
    if (isOpen && currentRow) {
      form.reset({
        title: `任务异常: ${currentRow.task_name}`,
        content: `任务ID: ${currentRow.id}\n异常描述: `,
      })
    }
  }, [isOpen, currentRow, form])

  const mutation = useMutation({
    mutationFn: createFeedback,
    onSuccess: () => {
      toast.success('异常已提交', {
        description: '我们会尽快处理您的反馈。',
      })
      setOpen(null)
    },
    onError: (error: any) => {
      toast.error('提交失败', {
        description: error.message || '无法提交异常。',
      })
    }
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    const data: CreateFeedbackData = {
      ...values,
      category: 'dispatcher_issue', // 强制类型为调度异常
    }
    mutation.mutate(data)
  }

  return (
    <Dialog open={isOpen} onOpenChange={(v) => !v && setOpen(null)}>
      <DialogContent className='sm:max-w-[500px]'>
        <DialogHeader>
          <DialogTitle>报告任务异常</DialogTitle>
          <DialogDescription>
            如果您在执行任务过程中遇到问题，请在此提交。
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-4'>
            <FormField
              control={form.control}
              name='title'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>标题</FormLabel>
                  <FormControl>
                    <Input placeholder='异常标题' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='content'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>详细描述</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder='请详细描述您遇到的问题...' 
                      className="min-h-[120px]"
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className='flex justify-end gap-2 pt-4'>
              <Button type='button' variant='outline' onClick={() => setOpen(null)}>
                取消
              </Button>
              <Button type='submit' disabled={mutation.isPending}>
                {mutation.isPending ? '提交中...' : '提交'}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

