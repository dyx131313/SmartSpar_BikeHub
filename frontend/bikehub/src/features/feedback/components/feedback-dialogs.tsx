import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Dialog,
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
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { useFeedback } from './feedback-provider'
import { createFeedback, updateFeedback } from '../api'
import { toast } from 'sonner'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/auth-store'

const createFormSchema = z.object({
  title: z.string().min(1, '标题不能为空'),
  content: z.string().min(1, '内容不能为空'),
  category: z.enum(['user_feedback', 'dispatcher_issue']).optional(),
})

const resolveFormSchema = z.object({
  status: z.enum(['pending', 'processing', 'resolved', 'closed']),
  resolution_notes: z.string().min(1, '处理备注不能为空'),
})

export function FeedbackDialogs() {
  const { open, setOpen, currentRow, setCurrentRow } = useFeedback()
  const queryClient = useQueryClient()
  const { user } = useAuthStore((state) => state.auth)

  const createForm = useForm<z.infer<typeof createFormSchema>>({
    resolver: zodResolver(createFormSchema),
    defaultValues: {
      title: '',
      content: '',
      category: user?.role === 'dispatcher' ? 'dispatcher_issue' : 'user_feedback',
    },
  })

  const resolveForm = useForm<z.infer<typeof resolveFormSchema>>({
    resolver: zodResolver(resolveFormSchema),
    defaultValues: {
      status: 'resolved',
      resolution_notes: '',
    },
  })

  const createMutation = useMutation({
    mutationFn: createFeedback,
    onSuccess: () => {
      toast.success('反馈提交成功')
      queryClient.invalidateQueries({ queryKey: ['feedbacks'] })
      setOpen(null)
      createForm.reset()
    },
    onError: (error: any) => {
      toast.error(error.message || '提交失败')
    },
  })

  const resolveMutation = useMutation({
    mutationFn: (data: z.infer<typeof resolveFormSchema>) => 
      updateFeedback(currentRow!.id, data),
    onSuccess: () => {
      toast.success('反馈处理成功')
      queryClient.invalidateQueries({ queryKey: ['feedbacks'] })
      setOpen(null)
      setCurrentRow(null)
      resolveForm.reset()
    },
    onError: (error: any) => {
      toast.error(error.message || '处理失败')
    },
  })

  function onCreateSubmit(values: z.infer<typeof createFormSchema>) {
    createMutation.mutate(values)
  }

  function onResolveSubmit(values: z.infer<typeof resolveFormSchema>) {
    resolveMutation.mutate(values)
  }

  return (
    <>
      {/* 创建反馈对话框 */}
      <Dialog open={open === 'create'} onOpenChange={(isOpen) => {
          if (!isOpen) setOpen(null)
      }}>
        <DialogContent className='sm:max-w-[425px]'>
          <DialogHeader>
            <DialogTitle>提交反馈</DialogTitle>
            <DialogDescription>
              请详细描述您遇到的问题或建议。
            </DialogDescription>
          </DialogHeader>
          <Form {...createForm}>
            <form onSubmit={createForm.handleSubmit(onCreateSubmit)} className='space-y-4'>
              <FormField
                control={createForm.control}
                name='title'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>标题</FormLabel>
                    <FormControl>
                      <Input placeholder='简要描述问题' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              {user?.role === 'admin' && (
                <FormField
                  control={createForm.control}
                  name='category'
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>类型</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder='选择反馈类型' />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value='user_feedback'>用户反馈</SelectItem>
                          <SelectItem value='dispatcher_issue'>调度异常</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              <FormField
                control={createForm.control}
                name='content'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>内容</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder='详细描述...' 
                        className='min-h-[100px]'
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type='submit' disabled={createMutation.isPending}>
                  {createMutation.isPending ? '提交中...' : '提交'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      {/* 查看详情对话框 */}
      <Dialog open={open === 'view'} onOpenChange={(isOpen) => {
          if (!isOpen) {
              setOpen(null)
              setCurrentRow(null)
          }
      }}>
        <DialogContent className='sm:max-w-[600px]'>
          <DialogHeader>
            <DialogTitle>反馈详情</DialogTitle>
          </DialogHeader>
          <div className='grid gap-4 py-4'>
             <div className='grid grid-cols-4 items-center gap-4'>
              <span className='font-bold'>标题:</span>
              <span className='col-span-3'>{currentRow?.title}</span>
            </div>
            <div className='grid grid-cols-4 items-center gap-4'>
              <span className='font-bold'>类型:</span>
              <span className='col-span-3'>{currentRow?.category_display}</span>
            </div>
            <div className='grid grid-cols-4 items-center gap-4'>
              <span className='font-bold'>状态:</span>
              <span className='col-span-3'>{currentRow?.status_display}</span>
            </div>
            <div className='grid grid-cols-4 items-start gap-4'>
              <span className='font-bold'>内容:</span>
              <span className='col-span-3 whitespace-pre-wrap'>{currentRow?.content}</span>
            </div>
             {currentRow?.resolution_notes && (
                <div className='grid grid-cols-4 items-start gap-4'>
                  <span className='font-bold'>处理备注:</span>
                  <span className='col-span-3 whitespace-pre-wrap text-green-600'>
                    {currentRow.resolution_notes}
                  </span>
                </div>
             )}
             {currentRow?.resolved_by && (
                <div className='grid grid-cols-4 items-center gap-4'>
                  <span className='font-bold'>处理人:</span>
                  <span className='col-span-3'>
                      {currentRow.resolver?.full_name || currentRow.resolver?.username}
                      <span className='ml-2 text-sm text-muted-foreground'>
                          ({new Date(currentRow.resolved_at!).toLocaleString()})
                      </span>
                  </span>
                </div>
             )}
          </div>
        </DialogContent>
      </Dialog>

      {/* 处理反馈对话框 */}
      <Dialog open={open === 'resolve'} onOpenChange={(isOpen) => {
          if (!isOpen) {
              setOpen(null)
              setCurrentRow(null)
          }
      }}>
        <DialogContent className='sm:max-w-[425px]'>
          <DialogHeader>
            <DialogTitle>处理反馈</DialogTitle>
            <DialogDescription>
              请填写处理结果和备注。
            </DialogDescription>
          </DialogHeader>
          <Form {...resolveForm}>
            <form onSubmit={resolveForm.handleSubmit(onResolveSubmit)} className='space-y-4'>
              <FormField
                control={resolveForm.control}
                name='status'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>状态</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder='选择状态' />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value='processing'>处理中</SelectItem>
                        <SelectItem value='resolved'>已解决</SelectItem>
                        <SelectItem value='closed'>已关闭</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={resolveForm.control}
                name='resolution_notes'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>处理备注</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder='请输入处理结果...' 
                        className='min-h-[100px]'
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <Button type='submit' disabled={resolveMutation.isPending}>
                  {resolveMutation.isPending ? '提交中...' : '提交'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </>
  )
}



