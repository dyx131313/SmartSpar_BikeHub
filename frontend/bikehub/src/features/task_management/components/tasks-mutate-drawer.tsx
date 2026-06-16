import { useEffect } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { SelectDropdown } from '@/components/select-dropdown'
import { type Task } from '../data/schema'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createTask, updateTask } from '../service'
import { toast } from 'sonner'

type TaskMutateDrawerProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentRow?: Task
}

// 优先级映射：前端字符串 <-> 后端数字
const priorityMap: Record<string, number> = { low: 1, medium: 2, high: 3 }
const priorityMapRev: Record<number, 'low' | 'medium' | 'high'> = { 1: 'low', 2: 'medium', 3: 'high' }

const formSchema = z.object({
  task_name: z.string().min(1, '请输入任务名称'),
  from_station_id: z.coerce.number().min(1, '请输入起始站点ID'),
  to_station_id: z.coerce.number().min(1, '请输入终点站点ID'),
  bike_count: z.coerce.number().min(1, '数量必须大于0'),
  priority: z.enum(['low', 'medium', 'high']),
  status: z.string().optional(),
  assigned_to: z.coerce.number().optional(),
})

type TaskForm = z.infer<typeof formSchema>

export function TasksMutateDrawer({
  open,
  onOpenChange,
  currentRow,
}: TaskMutateDrawerProps) {
  const isUpdate = !!currentRow
  const queryClient = useQueryClient()

  const form = useForm<TaskForm>({
    resolver: zodResolver(formSchema) as any,
    defaultValues: {
      task_name: '',
      from_station_id: 0,
      to_station_id: 0,
      bike_count: 0,
      priority: 'low',
      status: 'pending',
      assigned_to: 0,
    },
  })

  // 当打开抽屉或 currentRow 变化时，重置表单
  useEffect(() => {
    if (currentRow) {
      form.reset({
        task_name: currentRow.task_name || '',
        from_station_id: currentRow.from_station_id || 0,
        to_station_id: currentRow.to_station_id || 0,
        bike_count: currentRow.bike_count || 0,
        priority: (priorityMapRev[currentRow.priority as number] || 'low') as 'low' | 'medium' | 'high', // 数字转字符串
        status: currentRow.status || 'pending',
        assigned_to: currentRow.assigned_to || 0,
      })
    } else {
      form.reset({
        task_name: '',
        from_station_id: 0,
        to_station_id: 0,
        bike_count: 0,
        priority: 'low',
        status: 'pending',
        assigned_to: 0,
      })
    }
  }, [currentRow, open, form])

  const createMutation = useMutation({
    mutationFn: (data: any) => createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('任务创建成功')
      onOpenChange(false)
      form.reset()
    },
    onError: (error: any) => {
      toast.error('创建失败', { description: error.message || '请检查输入数据' })
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data: any) => updateTask(currentRow!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      toast.success('任务更新成功')
      onOpenChange(false)
    },
    onError: (error: any) => {
      toast.error('更新失败', { description: error.message })
    },
  })

  const onSubmit = (data: TaskForm) => {
    // 转换数据格式以匹配后端
    const payload = {
      ...data,
      priority: priorityMap[data.priority], // 字符串转数字
      assigned_to: data.assigned_to || null, // 0 或 undefined 转为 null
    }

    if (isUpdate) {
      updateMutation.mutate(payload)
    } else {
      createMutation.mutate(payload)
    }
  }

  return (
    <Sheet
      open={open}
      onOpenChange={(v) => {
        onOpenChange(v)
        form.reset()
      }}
    >
      <SheetContent className='flex flex-col overflow-y-auto'>
        <SheetHeader className='text-start'>
          <SheetTitle>{isUpdate ? '更新' : '创建'} 调度任务</SheetTitle>
          <SheetDescription>
            {isUpdate ? '更新调度任务信息。' : '添加新的调度任务。'}
            点击保存完成操作。
          </SheetDescription>
        </SheetHeader>
        <Form {...form}>
          <form
            id='tasks-form'
            onSubmit={form.handleSubmit(onSubmit)}
            className='flex-1 space-y-5 px-1 py-4'
          >
            <FormField
              control={form.control}
              name='task_name'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>任务名称</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder='请输入任务名称' />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name='from_station_id'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>起始站点ID</FormLabel>
                    <FormControl>
                      <Input type='number' {...field} placeholder='ID' />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name='to_station_id'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>终点站点ID</FormLabel>
                    <FormControl>
                      <Input type='number' {...field} placeholder='ID' />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name='bike_count'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>车辆数量</FormLabel>
                    <FormControl>
                      <Input type='number' {...field} placeholder='数量' />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name='assigned_to'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>执行人ID</FormLabel>
                    <FormControl>
                      <Input type='number' {...field} placeholder='用户ID' />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name='status'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>状态</FormLabel>
                  <SelectDropdown
                    defaultValue={field.value}
                    onValueChange={field.onChange}
                    placeholder='选择状态'
                    items={[
                      { label: '待办 (Pending)', value: 'pending' },
                      { label: '进行中 (In Progress)', value: 'in_progress' },
                      { label: '已完成 (Completed)', value: 'completed' },
                      { label: '已取消 (Cancelled)', value: 'cancelled' },
                      { label: '积压 (Backlog)', value: 'backlog' },
                    ]}
                  />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name='priority'
              render={({ field }) => (
                <FormItem className='relative'>
                  <FormLabel>优先级</FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className='flex flex-col space-y-1'
                    >
                      <FormItem className='flex items-center space-x-3 space-y-0'>
                        <FormControl>
                          <RadioGroupItem value='high' />
                        </FormControl>
                        <FormLabel className='font-normal'>高 (High)</FormLabel>
                      </FormItem>
                      <FormItem className='flex items-center space-x-3 space-y-0'>
                        <FormControl>
                          <RadioGroupItem value='medium' />
                        </FormControl>
                        <FormLabel className='font-normal'>中 (Medium)</FormLabel>
                      </FormItem>
                      <FormItem className='flex items-center space-x-3 space-y-0'>
                        <FormControl>
                          <RadioGroupItem value='low' />
                        </FormControl>
                        <FormLabel className='font-normal'>低 (Low)</FormLabel>
                      </FormItem>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </form>
        </Form>
        <SheetFooter className='gap-2'>
          <SheetClose asChild>
            <Button variant='outline'>关闭</Button>
          </SheetClose>
          <Button form='tasks-form' type='submit' disabled={createMutation.isPending || updateMutation.isPending}>
            {createMutation.isPending || updateMutation.isPending ? '保存中...' : '保存更改'}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
