import { useState } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate } from '@tanstack/react-router'
import { ArrowRight, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { apiPost } from '@/lib/api'
import { handleServerError } from '@/lib/handle-server-error'
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

const formSchema = z.object({
  identifier: z
    .string()
    .min(1, '请输入用户名或QQ邮箱')
    .max(100),
})

export function ForgotPasswordForm({
  className,
  ...props
}: React.HTMLAttributes<HTMLFormElement>) {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { identifier: '' },
  })

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setIsLoading(true)
    try {
      const payload = { identifier: data.identifier.trim() }
      const resp = await apiPost('/api/auth/forgot-password/request', payload)

      const msg =
        resp?.message ??
        'If the account exists and has a bound email, a verification code has been sent to that email'
      toast.success(msg)

      // 浣跨敤 sessionStorage 淇濆瓨璐﹀彿鏍囪瘑锛屼紶缁欭TP椤甸潰
      try {
        sessionStorage.setItem('reset_identifier', payload.identifier)
      } catch {
        // ignore
      }

      form.reset()
      navigate({ to: '/otp' })
    } catch (err) {
      handleServerError(err)
      toast.error('Failed to start password reset, please try again')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className={cn('grid gap-2', className)}
        {...props}
      >
        <FormField
          control={form.control}
          name='identifier'
          render={({ field }) => (
            <FormItem>
              <FormLabel>用户名/QQ邮箱</FormLabel>
              <FormControl>
                <Input placeholder='请输入用户名/QQ邮箱' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button className='mt-2' disabled={isLoading}>
          继续
          {isLoading ? <Loader2 className='animate-spin' /> : <ArrowRight />}
        </Button>
      </form>
    </Form>
  )
}
