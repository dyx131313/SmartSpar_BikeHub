import { useState } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from '@tanstack/react-router'
import { Loader2, LogIn } from 'lucide-react'
import { toast } from 'sonner'
import { IconFacebook, IconGithub } from '@/assets/brand-icons'
import { apiPost } from '@/lib/api'
import { setCookie } from '@/lib/cookies'
import { handleServerError } from '@/lib/handle-server-error'
import { useAuthStore } from '@/stores/auth-store'
import { sleep, cn } from '@/lib/utils'
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
  // username: z.string().min(2).max(100).trim().toLowerCase().transform((val) => val.replace(/\s+/g, '')),
  username: z.string().min(2).max(100).trim(),
  // .toLowerCase().transform((val) => val.replace(/\s+/g, '')),
  // email: z.email({
  //   error: (iss) => (iss.input === '' ? 'Please enter your email' : undefined),
  // }),
  password: z
    .string()
    .min(1, 'Please enter your password')
    .min(7, 'Password must be at least 7 characters long'),
})

interface UserAuthFormProps extends React.HTMLAttributes<HTMLFormElement> {
  redirectTo?: string
}

export function UserAuthForm({
  className,
  redirectTo,
  ...props
}: UserAuthFormProps) {
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  // const { auth } = useAuthStore()
  const setAccessToken = useAuthStore((s) => s.auth?.setAccessToken)
  const setUser = useAuthStore((s) => s.auth?.setUser)
  const readAuthState = () => useAuthStore.getState()?.auth

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  })

  function onSubmit(data: z.infer<typeof formSchema>) {
    // setIsLoading(true)

    // toast.promise(sleep(2000), {
    //   loading: 'Signing in...',
    //   success: () => {
    //     setIsLoading(false)

    //     // Mock successful authentication with expiry computed at success time
    //     const mockUser = {
    //       accountNo: 'ACC001',
    //       email: data.email,
    //       role: ['user'],
    //       exp: Date.now() + 24 * 60 * 60 * 1000, // 24 hours from now
    //     }

    //     // Set user and access token
    //     auth.setUser(mockUser)
    //     auth.setAccessToken('mock-access-token')

    //     // Redirect to the stored location or default to dashboard
    //     const targetPath = redirectTo || '/'
    //     navigate({ to: targetPath, replace: true })

    //     return `Welcome back, ${data.email}!`
    //   },
    //   error: 'Error',
    // })
    // 浣跨敤鐪熷疄 API 鐧诲綍
    console.log('onSubmit called', data)
      ; (async () => {
        setIsLoading(true)
        try {
          // console.log('calling apiPost /api/auth/login', { username: data.username })
          const payload = { username: data.username, password: data.password }
          const resp = await apiPost('/api/auth/login', payload)
          // console.log('login resp', resp)
          // console.log('useAuthStore.getState()', useAuthStore.getState()) 
          // const token = resp?.access_token ?? resp?.token ?? resp?.data?.token
          // if (token) {
          //   auth.setAccessToken(token)
          // }
          // if (resp?.user) {
          //   auth.setUser(resp.user)
          // }
          // const currentUser = useAuthStore.getState()?.auth?.user ?? resp?.user ?? null

          console.log('login resp', resp)
          const token =
            resp?.access_token ??
            // resp?.accessToken ??
            // resp?.token ??
            // resp?.data?.access_token ??
            // resp?.data?.accessToken ??
            // resp?.data?.token ??
            null


          if (token) {
            setAccessToken?.(token)
            console.log('setAccessToken called ->', token)
            try { localStorage.setItem('access_token', typeof token === 'string' ? token : String(token)) } catch { }
          } else {
            console.warn('No token extracted from login resp', resp)
          }

          const user = resp?.user ?? null
          if (user) {
            setUser?.(user)
            console.log('setUser called ->', user)
          } else {
            console.warn('No user in login resp', resp)
          }

          // const currentUser = readAuthState()?.user ?? user ?? null

          const displayName = user?.full_name ?? user?.username ?? user?.email
          const rolePart = user?.role
            ? Array.isArray(user.role)
              ? `(${user.role.join(', ')})`
              : `(${user.role})`
            : ''
          toast.success(`欢迎${displayName}${rolePart}`)

          const targetPath = redirectTo || '/'
          navigate({ to: targetPath, replace: true })
        } catch (err) {
          handleServerError(err)
          toast.error('Sign in failed')
        } finally {
          setIsLoading(false)
        }
      })()
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
              <FormLabel>用户名 / QQ邮箱</FormLabel>
              <FormControl>
                <Input placeholder='请输入用户名或 QQ 邮箱' {...field} />
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
                <PasswordInput placeholder='********' {...field} />
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
        {/* <Button className='mt-2' disabled={isLoading}> */}
        <Button type='submit' className='mt-2' disabled={isLoading}>
          {isLoading ? <Loader2 className='animate-spin' /> : <LogIn />}
          登录
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
        </div>

        <div className='grid grid-cols-2 gap-2'>
          <Button variant='outline' type='button' disabled={isLoading}>
            <IconGithub className='h-4 w-4' /> GitHub
          </Button>
          <Button variant='outline' type='button' disabled={isLoading}>
            <IconFacebook className='h-4 w-4' /> Facebook
          </Button>
        </div> */}
      </form>
    </Form>
  )
}
