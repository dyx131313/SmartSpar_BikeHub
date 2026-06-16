import { useState, type HTMLAttributes } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from '@tanstack/react-router'
import { Loader2, LogIn } from 'lucide-react'
import { toast } from 'sonner'
import { apiPost } from '@/lib/api'
import { handleServerError } from '@/lib/handle-server-error'
import { useAuthStore } from '@/stores/auth-store'
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

const formSchema = z.object({
  username: z.string().min(2, '请输入用户名或邮箱').max(100).trim(),
  password: z.string().min(1, '请输入密码'),
})

interface UserAuthFormProps extends HTMLAttributes<HTMLFormElement> {
  redirectTo?: string
}

export function UserAuthForm({
  className,
  redirectTo,
  ...props
}: UserAuthFormProps) {
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const setAccessToken = useAuthStore((s) => s.auth?.setAccessToken)
  const setUser = useAuthStore((s) => s.auth?.setUser)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  })

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setIsLoading(true)

    try {
      const resp = await apiPost('/api/auth/login', {
        username: data.username,
        password: data.password,
      })

      const token = resp?.access_token ?? null
      if (token) {
        const tokenValue = typeof token === 'string' ? token : String(token)
        setAccessToken?.(tokenValue)
        try {
          localStorage.setItem('access_token', tokenValue)
        } catch {
          // localStorage may be unavailable in restricted browser contexts.
        }
      }

      const user = resp?.user ?? null
      if (user) {
        setUser?.(user)

        if (user.role) {
          try {
            const role = typeof user.role === 'string' ? user.role : String(user.role)
            localStorage.setItem('role', role)
            localStorage.setItem('user_role', role)
            localStorage.setItem('user-role', role)
          } catch {
            // Role is also kept in auth store, so localStorage failures are non-fatal.
          }
        }
      }

      const displayName = user?.full_name ?? user?.username ?? user?.email ?? data.username
      const rolePart = user?.role
        ? Array.isArray(user.role)
          ? ` (${user.role.join(', ')})`
          : ` (${user.role})`
        : ''

      toast.success(`欢迎回来，${displayName}${rolePart}`)
      navigate({ to: redirectTo || '/', replace: true })
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
              <FormLabel>用户名 / 邮箱</FormLabel>
              <FormControl>
                <Input placeholder='请输入用户名或邮箱' autoComplete='username' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='password'
          render={({ field }) => (
            <FormItem className='relative'>
              <FormLabel>密码</FormLabel>
              <FormControl>
                <PasswordInput
                  placeholder='********'
                  autoComplete='current-password'
                  {...field}
                />
              </FormControl>
              <FormMessage />
              <Link
                to='/forgot-password'
                className='text-muted-foreground absolute end-0 -top-0.5 text-sm font-medium hover:opacity-75'
              >
                忘记密码？
              </Link>
            </FormItem>
          )}
        />
        <Button type='submit' className='mt-2' disabled={isLoading}>
          {isLoading ? <Loader2 className='animate-spin' /> : <LogIn />}
          登录
        </Button>
      </form>
    </Form>
  )
}
