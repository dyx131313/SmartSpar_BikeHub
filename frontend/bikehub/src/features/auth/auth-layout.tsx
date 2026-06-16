import { Logo } from '@/assets/logo'

type AuthLayoutProps = {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className='grid min-h-svh place-items-center bg-[var(--app-surface)] px-4'>
      <div className='mx-auto flex w-full max-w-[420px] flex-col justify-center space-y-4 py-8'>
        <div className='flex items-center justify-center'>
          <Logo className='me-2' />
          <h1 className='text-xl font-semibold'>智斗单车运营调度平台</h1>
        </div>
        {children}
      </div>
    </div>
  )
}
