import { optional, z } from 'zod'
import { useFieldArray, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from '@tanstack/react-router'
import { showSubmittedData } from '@/lib/show-submitted-data'
import { cn } from '@/lib/utils'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'
import { useAuthStore } from '@/stores/auth-store' 
import { apiPut, apiGet } from '@/lib/api'
import { F } from 'node_modules/@faker-js/faker/dist/airline-DF6RqYmq'

const profileFormSchema = z.object({
  username: z.string('请输入您的用户名。').optional(),
  email: z.string('请输入您的电子邮件地址。').optional(),
  full_name: z.string('请输入您的全名。').optional(),
  current_password: z.string().optional(),
  new_password: z.string().min(8, '新密码至少 8 字符').optional(),
  confirm_password: z.string().optional()
  // bio: z.string().max(160).min(4),
  // urls: z
  //   .array(
  //     z.object({
  //       value: z.url('Please enter a valid URL.'),
  //     })
  //   )
  //   .optional(),
})

type ProfileFormValues = z.infer<typeof profileFormSchema>

// This can come from your database or API.
const defaultValues: Partial<ProfileFormValues> = {
  // bio: 'I own a computer.',
  // urls: [
  //   { value: 'https://shadcn.com' },
  //   { value: 'http://twitter.com/shadcn' },
  // ],
  username: '',
  email: '',
  full_name: '',
}

export function ProfileForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues,
    // mode: 'onChange',
  })

  // const { fields, append } = useFieldArray({
  //   name: 'urls',
  //   control: form.control,
  // })
  const setUser = useAuthStore((s) => s.auth?.setUser)


  async function onSubmit(data: ProfileFormValues) {
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

      if(data.new_password && current_user){
        // if(!data.current_password){
        //   toast.error('当前密码不正确，无法修改密码')
        //   setIsSubmitting(false)
        //   return
        // }
        if(data.new_password !== data.confirm_password){
          toast.error('新密码与确认密码不匹配')
          setIsSubmitting(false)
          return
        }
      } 

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
    
    // 构建 PUT 所需的完整 payload：以后端返回的 current_user 为基础，只修改需要更新的字段
          const payload: any = {
            // 复制后端返回的字段，覆盖 full_name（或 name）为表单值
            ...current_user,
            // user_name: data.username ?? current_user.user_name ?? current_user.username,
            // email: data.email ?? current_user.email,
            // full_name: data.full_name ?? current_user.full_name ?? current_user.name,
            // // 仅在表单提供新密码时才包含 password 字段
            ...(data.new_password ? { password: data.new_password } : {}),
            ...(data.current_password ? { current_password: data.current_password } : {}),
            ...(data.email ? { email: data.email } : {}),
            ...(data.username ? { username: data.username } : {}),
            ...(data.full_name ? { full_name: data.full_name } : {}),
          }

      // console.log('Update payload:', payload)


      // 调用后端 PUT 更新指定用户（注意 API 路径需要 id）
      const resp = await apiPut(`/api/users/${encodeURIComponent(String(id))}`, payload)

      // apiPut 已经做了兼容解析，resp 应为更新后的用户数据或包装对象
      const updatedUser = resp?.user ?? resp?.data ?? resp ?? null
      if (updatedUser) {
        setUser?.(updatedUser)
        toast.success('账户资料已更新')
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
          name='username'
          render={({ field }) => (
            <FormItem>
              <FormLabel>用户名称</FormLabel>
              <FormControl>
                <Input placeholder='请输入新用户名称' {...field} />
              </FormControl>
              <FormDescription>
                这是您的公开显示名称。可以是您的真实姓名或化名。
                {/* 您只能每 30 天更改一次。 */}
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='full_name'
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
        <FormField
          control={form.control}
          name='email'
          render={({ field }) => (
            <FormItem>
              <FormLabel>邮箱</FormLabel>
              <FormControl>
                {/* 将 Select 改为可输入的邮箱输入框 */}
                <Input type='email' placeholder='请输入邮箱' {...field} />
              </FormControl>
              <FormDescription>
                您可以在{' '}
                <Link to='/'>邮箱设置</Link>中管理已验证的邮箱地址。
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='current_password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>当前密码</FormLabel>
              <FormControl>
                <Input
                  type='password'
                  placeholder='输入当前密码以确认更改'
                  {...field}
                />
              </FormControl>
              <FormDescription>
                为了安全起见，请输入您的当前密码以确认更改。
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='new_password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>新密码</FormLabel>
              <FormControl>
                <Input
                  type='password'
                  placeholder='输入新密码（可选）'
                  {...field}
                />
              </FormControl>
              <FormDescription>
                如果您想更改密码，请在此输入新密码。否则请留空。  
                新密码至少需要 8 个字符。
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='confirm_password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>确认新密码</FormLabel>
              <FormControl>
                <Input
                  type='password'
                  placeholder='再次输入新密码以确认'
                  {...field}
                />
              </FormControl>
              <FormDescription>
                请再次输入新密码以确认无误。
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* <FormField
          control={form.control}
          name='bio'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Textarea
                  placeholder='Tell us a little bit about yourself'
                  className='resize-none'
                  {...field}
                />
              </FormControl>
              <FormDescription>
                You can <span>@mention</span> other users and organizations to
                link to them.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        /> */}
        {/* <div>
          {fields.map((field, index) => (
            <FormField
              control={form.control}
              key={field.id}
              name={`urls.${index}.value`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel className={cn(index !== 0 && 'sr-only')}>
                    URLs
                  </FormLabel>
                  <FormDescription className={cn(index !== 0 && 'sr-only')}>
                    Add links to your website, blog, or social media profiles.
                  </FormDescription>
                  <FormControl className={cn(index !== 0 && 'mt-1.5')}>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          ))}
          <Button
            type='button'
            variant='outline'
            size='sm'
            className='mt-2'
            onClick={() => append({ value: '' })}
          >
            Add URL
          </Button>
        </div> */}
        <Button type='submit' disabled={isSubmitting}>{isSubmitting ? '保存中...' : '更新账户'}</Button>
      </form>
    </Form>
  )
}
