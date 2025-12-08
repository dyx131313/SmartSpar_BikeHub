// import { Link } from '@tanstack/react-router'
// import {
//   Card,
//   CardContent,
//   CardDescription,
//   CardFooter,
//   CardHeader,
//   CardTitle,
// } from '@/components/ui/card'
// import { AuthLayout } from '../auth-layout'
// import { SignUpForm } from './components/sign-up-form'

// export function SignUp() {
//   return (
//     <AuthLayout>
//       <Card className='gap-4'>
//         <CardHeader>
//           <CardTitle className='text-lg tracking-tight'>
//             Create an account
//           </CardTitle>
//           <CardDescription>
//             Enter your email and password to create an account. <br />
//             Already have an account?{' '}
//             <Link
//               to='/sign-in-2'
//               className='hover:text-primary underline underline-offset-4'
//             >
//               Sign In
//             </Link>
//           </CardDescription>
//         </CardHeader>
//         <CardContent>
//           <SignUpForm />
//         </CardContent>
//         <CardFooter>
//           <p className='text-muted-foreground px-8 text-center text-sm'>
//             By creating an account, you agree to our{' '}
//             <a
//               href='/terms'
//               className='hover:text-primary underline underline-offset-4'
//             >
//               Terms of Service
//             </a>{' '}
//             and{' '}
//             <a
//               href='/privacy'
//               className='hover:text-primary underline underline-offset-4'
//             >
//               Privacy Policy
//             </a>
//             .
//           </p>
//         </CardFooter>
//       </Card>
//     </AuthLayout>
//   )
// }

// ...existing code...
import { Logo } from '@/assets/logo'
import { cn } from '@/lib/utils'
import dashboardDark from '../sign-in/assets/dashboard-dark.png'
import dashboardLight from '../sign-in/assets/dashboard-light.png'
import { SignUpForm } from './components/sign-up-form'
import { Link } from '@tanstack/react-router'

export function SignUp() {
  return (
    <div className='relative container grid h-svh flex-col items-center justify-center lg:max-w-none lg:grid-cols-2 lg:px-0'>
      <div className='lg:p-8'>
        <div className='mx-auto flex w-full flex-col justify-center space-y-2 py-8 sm:w-[480px] sm:p-8'>
          <div className='mb-4 flex items-center justify-center'>
            {/* <Logo className='me-2' /> */}
            <h1 className='text-xl font-medium'>智斗单车</h1>
          </div>
        </div>
        <div className='mx-auto flex w-full max-w-sm flex-col justify-center space-y-2'>
          <div className='flex flex-col space-y-2 text-start'>
            <h2 className='text-lg font-semibold tracking-tight'>创建账户</h2>
            <p className='text-muted-foreground text-sm'>
              请输入您的邮箱和密码以创建账户
              <span className='ms-2'>
                已有账号？{' '}
                <Link
                  to='/sign-in-2'
                  className='hover:text-primary underline underline-offset-4'
                >
                  立即登录
                </Link>
              </span>
            </p>
          </div>
          <SignUpForm />
          <p className='text-muted-foreground px-8 text-center text-sm'>
            点击注册即表示您同意我们的{' '}
            <a
              href='/terms'
              className='hover:text-primary underline underline-offset-4'
            >
              服务条款
            </a>{' '}
            和{' '}
            <a
              href='/privacy'
              className='hover:text-primary underline underline-offset-4'
            >
              隐私政策
            </a>
            .
          </p>
        </div>
      </div>

      <div
        className={cn(
          'bg-muted relative h-full overflow-hidden max-lg:hidden',
          '[&>img]:absolute [&>img]:top-[15%] [&>img]:left-20 [&>img]:h-full [&>img]:w-full [&>img]:object-cover [&>img]:object-top-left [&>img]:select-none'
        )}
      >
        <img
          src={dashboardLight}
          className='dark:hidden'
          width={1024}
          height={1151}
          alt='Illustration'
        />
        <img
          src={dashboardDark}
          className='hidden dark:block'
          width={1024}
          height={1138}
          alt='Illustration'
        />
      </div>
    </div>
  )
}
// ...existing code...
