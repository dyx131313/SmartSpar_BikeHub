import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { CaretSortIcon, CheckIcon } from '@radix-ui/react-icons'
import { zodResolver } from '@hookform/resolvers/zod'
import { showSubmittedData } from '@/lib/show-submitted-data'
import { cn } from '@/lib/utils'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { DatePicker } from '@/components/date-picker'
import { toast } from 'sonner'
import { useAuthStore } from '@/stores/auth-store' 
import { apiPut, apiGet } from '@/lib/api'

const languages = [
  { label: 'English', value: 'en' },
  { label: 'French', value: 'fr' },
  { label: 'German', value: 'de' },
  { label: 'Spanish', value: 'es' },
  { label: 'Portuguese', value: 'pt' },
  { label: 'Russian', value: 'ru' },
  { label: 'Japanese', value: 'ja' },
  { label: 'Korean', value: 'ko' },
  { label: 'Chinese', value: 'zh' },
] as const

const accountFormSchema = z.object({
  name: z
    .string()
    .min(1, 'Please enter your name.')
    .min(2, 'Name must be at least 2 characters.')
    .max(30, 'Name must not be longer than 30 characters.'),
  // dob: z.date('Please select your date of birth.'),
  // language: z.string('Please select a language.'),
})

type AccountFormValues = z.infer<typeof accountFormSchema>

// This can come from your database or API.
const defaultValues: Partial<AccountFormValues> = {
  name: '',
}

export function AccountForm() {
  const [isSubmitting, setIsSubmitting] = useState(false) // 新增 loading 状态
  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountFormSchema),
    defaultValues,
  })

  const setUser = useAuthStore((s) => s.auth?.setUser)

  async function onSubmit(data: AccountFormValues) {
    setIsSubmitting(true)
    try {
      // 先从后端拉取当前完整用户数据（保证 PUT 请求体字段完整，避免必须字段缺失）
      const current = await apiGet('/api/users/profile')
      // console.log('Current user data:', current)
      if (!current) {
        toast.error('无法读取当前用户信息，更新失败')
        return
      }

      const current_user = current.data

      // 从返回中尽量取到用户 id（兼容多种字段名）
      const id =
        current_user?.id ??
        current_user?._id ??
        current_user?.accountNo ??
        current_user?.account_id ??
        current_user?.username
      if (!id) {
        toast.error('无法确定用户 ID，更新失败')
        return
      }
    
    // 构建 PUT 所需的完整 payload：以后端返回的 current 为基础，只修改需要更新的字段
      const payload: any = {
        // 复制后端返回的字段，覆盖 full_name（或 name）为表单值
        ...current,
        full_name: data.name ?? current.full_name ?? current.name,
      }

      // 调用后端 PUT 更新指定用户（注意 API 路径需要 id）
      const resp = await apiPut(`/api/users/${encodeURIComponent(String(id))}`, payload)

      // apiPut 已经做了兼容解析，resp 应为更新后的用户数据或包装对象
      const updatedUser = resp?.user ?? resp?.data ?? resp ?? null
      if (updatedUser) {
        setUser?.(updatedUser)
        toast.success('账户信息已更新')
        setTimeout(() => {
          try { window.location.reload() } catch { /* ignore */ }
        }, 500)
      } else {
        toast.success('更新已提交')
      }
    } catch (err: any) {
      console.error('Update account failed', err)
      toast.error(err?.message ?? '更新失败，请重试')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-8'>
        <FormField
          control={form.control}
          name='name'
          render={({ field }) => (
            <FormItem>
              <FormLabel>姓名</FormLabel>
              <FormControl>
                <Input placeholder='请输入姓名' {...field} />
              </FormControl>
              <FormDescription>
                您的真实姓名或化名。
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* <FormField
          control={form.control}
          name='dob'
          render={({ field }) => (
            <FormItem className='flex flex-col'>
              <FormLabel>Date of birth</FormLabel>
              <DatePicker selected={field.value} onSelect={field.onChange} />
              <FormDescription>
                Your date of birth is used to calculate your age.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='language'
          render={({ field }) => (
            <FormItem className='flex flex-col'>
              <FormLabel>Language</FormLabel>
              <Popover>
                <PopoverTrigger asChild>
                  <FormControl>
                    <Button
                      variant='outline'
                      role='combobox'
                      className={cn(
                        'w-[200px] justify-between',
                        !field.value && 'text-muted-foreground'
                      )}
                    >
                      {field.value
                        ? languages.find(
                            (language) => language.value === field.value
                          )?.label
                        : 'Select language'}
                      <CaretSortIcon className='ms-2 h-4 w-4 shrink-0 opacity-50' />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent className='w-[200px] p-0'>
                  <Command>
                    <CommandInput placeholder='Search language...' />
                    <CommandEmpty>No language found.</CommandEmpty>
                    <CommandGroup>
                      <CommandList>
                        {languages.map((language) => (
                          <CommandItem
                            value={language.label}
                            key={language.value}
                            onSelect={() => {
                              form.setValue('language', language.value)
                            }}
                          >
                            <CheckIcon
                              className={cn(
                                'size-4',
                                language.value === field.value
                                  ? 'opacity-100'
                                  : 'opacity-0'
                              )}
                            />
                            {language.label}
                          </CommandItem>
                        ))}
                      </CommandList>
                    </CommandGroup>
                  </Command>
                </PopoverContent>
              </Popover>
              <FormDescription>
                This is the language that will be used in the dashboard.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        /> */}
        <Button type='submit' disabled={isSubmitting}>{isSubmitting ? '保存中...' : '更新账户'}</Button>
      </form>
    </Form>
  )
}
