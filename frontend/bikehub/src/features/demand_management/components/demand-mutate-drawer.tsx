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
import { Checkbox } from '@/components/ui/checkbox'
import { type Demand } from '../data/schema'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createDemand, updateDemand } from '../service'
import { toast } from 'sonner'
import { stationTypes, weatherTypes } from '../data/data'

type DemandMutateDrawerProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentRow?: Demand
}

const formSchema = z.object({
  timestamp: z.string().min(1, '请选择时间'),
  station_id: z.coerce.number().min(1, '请输入站点ID'),
  weekday: z.coerce.number().min(1).max(7, '星期必须在1-7之间'),
  is_holiday: z.boolean(),
  weather: z.string().min(1, '请选择天气'),
  temp: z.coerce.number(),
  demand: z.coerce.number().min(0, '需求量必须大于等于0'),
})

type DemandForm = z.infer<typeof formSchema>

export function DemandMutateDrawer({
  open,
  onOpenChange,
  currentRow,
}: DemandMutateDrawerProps) {
  const isUpdate = !!currentRow
  const queryClient = useQueryClient()

  const form = useForm<DemandForm>({
    resolver: zodResolver(formSchema) as any,
    defaultValues: {
      timestamp: '',
      station_id: 0,
      weekday: 1,
      is_holiday: false,
      weather: '',
      temp: 0,
      demand: 0,
    },
  })

  useEffect(() => {
    if (currentRow) {
      form.reset({
        timestamp: currentRow.timestamp ? new Date(currentRow.timestamp).toISOString().slice(0, 16) : '',
        station_id: currentRow.station_id,
        weekday: currentRow.weekday,
        is_holiday: currentRow.is_holiday,
        weather: currentRow.weather,
        temp: currentRow.temp,
        demand: currentRow.demand,
      })
    } else {
      form.reset({
        timestamp: new Date().toISOString().slice(0, 16),
        station_id: 0,
        weekday: 1,
        is_holiday: false,
        weather: '',
        temp: 0,
        demand: 0,
      })
    }
  }, [currentRow, open, form])

  const createMutation = useMutation({
    mutationFn: (data: any) => createDemand(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['demands'] })
      toast.success('需求数据已创建')
      onOpenChange(false)
      form.reset()
    },
    onError: (error: any) => {
      toast.error('创建失败', { description: error.message })
    }
  })

  const updateMutation = useMutation({
    mutationFn: (data: any) => updateDemand(currentRow!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['demands'] })
      toast.success('需求数据已更新')
      onOpenChange(false)
    },
    onError: (error: any) => {
      toast.error('更新失败', { description: error.message })
    }
  })

  const onSubmit = (data: DemandForm) => {
    const payload = {
      ...data,
      // 直接使用表单中的时间字符串（本地时间格式 YYYY-MM-DDTHH:mm），
      // 避免 toISOString() 转换为 UTC 导致的时间偏差和后端解析问题
      timestamp: data.timestamp
    }

    if (isUpdate) {
      updateMutation.mutate(payload)
    } else {
      createMutation.mutate(payload)
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className='flex flex-col'>
        <SheetHeader>
          <SheetTitle>{isUpdate ? '编辑需求数据' : '创建需求数据'}</SheetTitle>
          <SheetDescription>
            {isUpdate
              ? '修改需求数据详情。'
              : '填写以下信息以创建新的需求数据。'}
          </SheetDescription>
        </SheetHeader>
        <Form {...form}>
          <form
            id='demand-form'
            onSubmit={form.handleSubmit(onSubmit)}
            className='flex-1 space-y-5 overflow-y-auto p-1'
          >
            <FormField
              control={form.control}
              name='timestamp'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>时间</FormLabel>
                  <FormControl>
                    <Input type='datetime-local' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='station_id'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>站点ID</FormLabel>
                  <FormControl>
                    <Input type='number' {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {/* station_type removed: now derived from station_id on backend */}
            <div className='flex gap-4'>
              <FormField
                control={form.control}
                name='weekday'
                render={({ field }) => (
                  <FormItem className='flex-1'>
                    <FormLabel>星期 (1-7)</FormLabel>
                    <FormControl>
                      <Input type='number' min={1} max={7} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name='is_holiday'
                render={({ field }) => (
                  <FormItem className='flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 shadow'>
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className='space-y-1 leading-none'>
                      <FormLabel>
                        节假日
                      </FormLabel>
                    </div>
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name='weather'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>天气</FormLabel>
                  <FormControl>
                    <SelectDropdown
                      defaultValue={field.value}
                      onValueChange={field.onChange}
                      placeholder='选择天气'
                      items={weatherTypes}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className='flex gap-4'>
              <FormField
                control={form.control}
                name='temp'
                render={({ field }) => (
                  <FormItem className='flex-1'>
                    <FormLabel>温度 (°C)</FormLabel>
                    <FormControl>
                      <Input type='number' step='0.1' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name='demand'
                render={({ field }) => (
                  <FormItem className='flex-1'>
                    <FormLabel>需求量</FormLabel>
                    <FormControl>
                      <Input type='number' {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </form>
        </Form>
        <SheetFooter className='gap-2 pt-2 sm:space-x-0'>
          <SheetClose asChild>
            <Button type='button' variant='outline'>
              取消
            </Button>
          </SheetClose>
          <Button
            type='submit'
            form='demand-form'
            disabled={isUpdate ? updateMutation.isPending : createMutation.isPending}
          >
            {isUpdate ? '保存更改' : '创建'}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
