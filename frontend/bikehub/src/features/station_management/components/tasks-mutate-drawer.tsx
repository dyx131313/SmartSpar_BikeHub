import React from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import MapPicker from './map-picker'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import { station_type } from '../data/data'
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
    resolver: zodResolver(formSchema) as any,
    defaultValues: currentRow ?? {
      name: '',
      station_type: '',
      latitude: 31.286054,
      longitude: 121.215252,
      capacity: 0,
      description: '',
    },
  })

  const createMutation = useMutation({
    mutationFn: createStation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stations'] })
      toast.success('站点创建成功', {
        description: '新的站点已成功创建。',
      })
      onOpenChange(false)
      form.reset()
    },
    onError: (error: any) => {
      toast.error('错误', {
        description: error.message || '创建站点失败。',
      })
    }
  })

  const updateMutation = useMutation({
    mutationFn: (data: TaskForm) => updateStation(currentRow!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stations'] })
      toast.success('站点更新成功', {
        description: '站点已成功更新。',
      })
      onOpenChange(false)
      form.reset()
    },
    onError: (error: any) => {
      toast.error('错误', {
        description: error.message || '更新站点失败。',
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

  const initLat = (form.getValues('latitude') as number) ?? 0
  const initLng = (form.getValues('longitude') as number) ?? 0
  const mapInitial = { latitude: initLat, longitude: initLng }

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
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder='选择站点类型' />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {station_type.map((t) => (
                        <SelectItem key={t.value} value={t.value}>
                          {t.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
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

            <div>
              <FormLabel className='mb-2'>在地图上选择位置</FormLabel>
              <div className='rounded-md overflow-hidden border'>
                <MapPicker
                  key={`${mapInitial.latitude}-${mapInitial.longitude}`}
                  initial={mapInitial}
                  height={280}
                  onSelect={(lat, lng) => {
                    form.setValue('latitude', lat, { shouldValidate: true, shouldDirty: true })
                    form.setValue('longitude', lng, { shouldValidate: true, shouldDirty: true })
                  }}
                />
              </div>
            </div>
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
        {/* inline MapPicker embedded above in the form */}
      </SheetContent>
    </Sheet>
  )
}
