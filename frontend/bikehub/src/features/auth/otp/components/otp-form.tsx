import { useState } from 'react'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate } from '@tanstack/react-router'
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
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
  InputOTPSeparator,
} from '@/components/ui/input-otp'
import { PasswordInput } from '@/components/password-input'

const formSchema = z
  .object({
    otp: z
      .string()
      .min(6, 'Please enter the 6-digit code')
      .max(6, 'Please enter the 6-digit code'),
    password: z
      .string()
      .min(7, 'Password must be at least 7 characters')
      .max(100, 'Password is too long'),
    confirmPassword: z
      .string()
      .min(7, 'Please re-enter your password')
      .max(100, 'Password is too long'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "The two passwords don't match",
    path: ['confirmPassword'],
  })

type OtpFormProps = React.HTMLAttributes<HTMLFormElement>

export function OtpForm({ className, ...props }: OtpFormProps) {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { otp: '', password: '', confirmPassword: '' },
  })

   
  const otp = form.watch('otp')

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setIsLoading(true)
    try {
      let identifier: string | null = null
      try {
        identifier = sessionStorage.getItem('reset_identifier')
      } catch {
        identifier = null
      }

      if (!identifier) {
        toast.error('Password reset session has expired, please start again')
        navigate({ to: '/forgot-password', replace: true })
        return
      }

      const payload = {
        identifier,
        code: data.otp,
        new_password: data.password,
      }

      await apiPost('/api/auth/forgot-password/reset', payload)

      try {
        sessionStorage.removeItem('reset_identifier')
      } catch {
        // ignore
      }

      toast.success('Password reset successful, please log in with your new password')
      navigate({ to: '/sign-in', replace: true })
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
        className={cn('grid gap-2', className)}
        {...props}
      >
        <FormField
          control={form.control}
          name='otp'
          render={({ field }) => (
            <FormItem>
              <FormLabel className='sr-only'>One-Time Password</FormLabel>
              <FormControl>
                <InputOTP
                  maxLength={6}
                  {...field}
                  containerClassName='justify-between sm:[&>[data-slot="input-otp-group"]>div]:w-12'
                >
                  <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                  </InputOTPGroup>
                  <InputOTPSeparator />
                  <InputOTPGroup>
                    <InputOTPSlot index={2} />
                    <InputOTPSlot index={3} />
                  </InputOTPGroup>
                  <InputOTPSeparator />
                  <InputOTPGroup>
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                  </InputOTPGroup>
                </InputOTP>
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
              <FormLabel>New password</FormLabel>
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
              <FormLabel>Confirm new password</FormLabel>
              <FormControl>
                <PasswordInput placeholder='********' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button className='mt-2' disabled={otp.length < 6 || isLoading}>
          Reset password
        </Button>
      </form>
    </Form>
  )
}
