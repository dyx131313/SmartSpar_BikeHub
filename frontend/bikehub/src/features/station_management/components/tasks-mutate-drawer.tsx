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
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { type Station } from '../data/schema'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createStation, updateStation } from '../service'
import { toast } from 'sonner'

type TaskMutateDrawerProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentRow?: Station
}

const formSchema = z.object({
  name: z.string().min(1, '站点名称是必填项.'),
  station_type: z.string().min(1, '站点类型是必填项.'),
  latitude: z.coerce
    .number()
    .min(-90, '纬度必须在 -90 到 90 之间.')
    .max(90, '纬度必须在 -90 到 90 之间.'),
  longitude: z.coerce
    .number()
    .min(-180, '经度必须在 -180 到 180 之间.')
    .max(180, '经度必须在 -180 到 180 之间.'),
  capacity: z.coerce
    .number()
    .min(0, '容量不能为负数.'),
  description: z.string().min(1, '描述是必填项.'),
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
    resolver: zodResolver(formSchema),
    defaultValues: currentRow ?? {
      name: '',
      station_type: '',
      latitude: 0,
      longitude: 0,
      capacity: 0,
      description: '',
    },
  })

  const createMutation = useMutation({
    mutationFn: createStation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stations'] })
      toast.success('Station created', {
        description: 'The new station has been created successfully.',
      })
      onOpenChange(false)
      form.reset()
    },
    onError: (error: any) => {
      toast.error('Error', {
        description: error.message || 'Failed to create station.',
      })
    }
  })

  const updateMutation = useMutation({
    mutationFn: (data: TaskForm) => updateStation(currentRow!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stations'] })
      toast.success('Station updated', {
        description: 'The station has been updated successfully.',
      })
      onOpenChange(false)
      form.reset()
    },
    onError: (error: any) => {
      toast.error('Error', {
        description: error.message || 'Failed to update station.',
      })
    }
  })

  const onSubmit = (data: TaskForm) => {
    if (isUpdate) {
      updateMutation.mutate(data)
    } else {
      createMutation.mutate(data)
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
      <SheetContent className='flex flex-col'>
        <SheetHeader className='text-start'>
          <SheetTitle>{isUpdate ? '更新' : '创建'} 站点</SheetTitle>
          <SheetDescription>
            {isUpdate
              ? '更新站点信息。'
              : '添加新的站点信息。'}
            点击保存完成操作。
          </SheetDescription>
        </SheetHeader>
        <Form {...form}>
          <form
            id='tasks-form'
            onSubmit={form.handleSubmit(onSubmit)}
            className='flex-1 space-y-6 overflow-y-auto px-4'
          >
            <FormField
              control={form.control}
              name='name'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>站点名称</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder='输入站点名称' />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='station_type'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>站点类型</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder='输入站点类型' />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='latitude'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>纬度</FormLabel>
                  <FormControl>
                    <Input
                      type='number'
                      step='any'
                      {...field}
                      placeholder='输入纬度'
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='longitude'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>经度</FormLabel>
                  <FormControl>
                    <Input
                      type='number'
                      step='any'
                      {...field}
                      placeholder='输入经度'
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='capacity'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>容量</FormLabel>
                  <FormControl>
                    <Input
                      type='number'
                      {...field}
                      placeholder='输入容量'
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='description'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>描述</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder='输入描述' />
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
          <Button form='tasks-form' type='submit'>
            保存更改
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
