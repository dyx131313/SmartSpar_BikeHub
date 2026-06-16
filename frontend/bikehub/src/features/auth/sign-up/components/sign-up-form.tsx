import { useState } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { IconFacebook, IconGithub } from '@/assets/brand-icons'
import { cn } from '@/lib/utils'
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
import { PasswordInput } from '@/components/password-input'

import { apiPost } from '@/lib/api'
import { handleServerError } from '@/lib/handle-server-error'
import { useAuthStore } from '@/stores/auth-store'
import { useNavigate } from '@tanstack/react-router'



const formSchema = z
  .object({
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters')
      .max(20, 'Username must be at most 20 characters')
      .trim(),
    email: z
      .string()
      .email({
        message: 'Please enter a valid email address',
      }),
    password: z
      .string()
      .min(1, 'Please enter your password'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  })

export function SignUpForm({
  className,
  ...props
}: React.HTMLAttributes<HTMLFormElement>) {
  const [isLoading, setIsLoading] = useState(false)

  const setAccessToken = useAuthStore((s) => s.auth.setAccessToken)
  const setUser = useAuthStore((s) => s.auth.setUser)
  const navigate = useNavigate()

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  })

  // function onSubmit(data: z.infer<typeof formSchema>) {
  //   setIsLoading(true)
  //   // // eslint-disable-next-line no-console
  //   // console.log(data)

  //   // setTimeout(() => {
  //   //   setIsLoading(false)
  //   // }, 3000)
  //     setIsLoading(true)
  //   try {
  //     const payload = { email: data.email, password: data.password, name: data.name }
  //     const resp = await apiPost('/api/auth/register', payload)
  //     // 鏈熸湜鍚庣杩斿洖 { user, token }
  //     if (resp?.token) {
  //       setAccessToken(resp.token)
  //     }
  //     if (resp?.user) {
  //       setUser(resp.user)
  //     }
  //     // 璺宠浆鍒扮櫥褰曢〉鎴栭椤?
  //     navigate({ to: '/sign-in-2' })
  //   } catch (err) {
  //     handleServerError(err)
  //   } finally {
  //     setIsLoading(false)
  //   }
  // }

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setIsLoading(true)
    try {
      const payload = {
        username: data.username.trim(),
        email: data.email.trim(),
        password: data.password,
      }
      const resp = await apiPost('/api/auth/register', payload)

      const token =
        resp?.access_token ??
        resp?.accessToken ??
        resp?.token ??
        resp?.data?.access_token ??
        resp?.data?.accessToken ??
        resp?.data?.token ??
        null

      if (token) {
        setAccessToken(token)
        try { localStorage.setItem('access_token', typeof token === 'string' ? token : String(token)) } catch {}
      }
      if (resp?.user) {
        setUser(resp.user)
        if (resp.user.role) {
          const roleStr = typeof resp.user.role === 'string' ? resp.user.role : String(resp.user.role)
          try {
            localStorage.setItem('role', roleStr)
            localStorage.setItem('user_role', roleStr)
            localStorage.setItem('user-role', roleStr)
          } catch {}
        }
      }

      navigate({ to: '/help-center', replace: true })
    } catch (err) {
      handleServerError(err)
    } finally {
      setIsLoading(false)
    }
  }
  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className={cn('grid gap-3', className)}
        {...props}
      >
        <FormField
          control={form.control}
          name='username'
          render={({ field }) => (
            <FormItem>
              <FormLabel>用户名</FormLabel>
              <FormControl>
                <Input placeholder='请输入用户名' {...field} />
              </FormControl>
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
                <Input placeholder='例如：123456@qq.com' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>密码</FormLabel>
              <FormControl>
                <PasswordInput placeholder='********' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='confirmPassword'
          render={({ field }) => (
            <FormItem>
              <FormLabel>确认密码</FormLabel>
              <FormControl>
                <PasswordInput placeholder='********' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button className='mt-2' disabled={isLoading}>
          注册
        </Button>

        {/* <div className='relative my-2'>
          <div className='absolute inset-0 flex items-center'>
            <span className='w-full border-t' />
          </div>
          <div className='relative flex justify-center text-xs uppercase'>
            <span className='bg-background text-muted-foreground px-2'>
              Or continue with
            </span>
          </div>
        </div> */}

        {/* <div className='grid grid-cols-2 gap-2'>
          <Button
            variant='outline'
            className='w-full'
            type='button'
            disabled={isLoading}
          >
            <IconGithub className='h-4 w-4' /> GitHub
          </Button>
          <Button
            variant='outline'
            className='w-full'
            type='button'
            disabled={isLoading}
          >
            <IconFacebook className='h-4 w-4' /> Facebook
          </Button>
        </div> */}
      </form>
    </Form>
  )
}
