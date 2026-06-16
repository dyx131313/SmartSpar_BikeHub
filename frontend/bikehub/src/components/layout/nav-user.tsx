  import { Link } from '@tanstack/react-router'
  import { useEffect, useState } from 'react'
  import {
    BadgeCheck,
    Bell,
    ChevronsUpDown,
    CreditCard,
    LogOut,
    LogIn,
    MessageSquare,
  } from 'lucide-react'
  import { useFeedback } from '@/features/feedback/components/feedback-provider'
  import useDialogState from '@/hooks/use-dialog-state'
  import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from '@/components/ui/dropdown-menu'
  import {
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    useSidebar,
  } from '@/components/ui/sidebar'
  import { SignOutDialog } from '@/components/sign-out-dialog'
  import { useAuthStore } from '@/stores/auth-store'
  import { apiGet, readToken, buildStaticUrl } from '@/lib/api'

  // function isJwtValid(token?: string) {
  //   if (!token || token.split('.').length !== 3) return false
  //   try {
  //     const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
  //     if (!payload || !payload.exp) return true // 没有 exp 就无法本地判断，返回 true 由后端判断
  //     const now = Math.floor(Date.now() / 1000)
  //     return payload.exp > now
  //   } catch {
  //     return false
  //   }
  // }


  type NavUserProps = {
    user?: {
      name?: string
      email?: string
      // avatar?: string
      // 兼容后端更多字段
      username?: string
      full_name?: string
    }
  }

  function getInitials(name?: string) {
    if (!name) return 'SN'
    const parts = name.trim().split(/\s+/)
    return (parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? parts[0]?.[1] ?? '')
  }

  export function NavUser() {
    // const { isMobile } = useSidebar()

    // 读取侧栏 state，判断是否折叠
    const { isMobile, state } = useSidebar()
    const [open, setOpen] = useDialogState()
    const feedback = useFeedback()


      // 从全局 store 读取 user（只使用 store 的 user；若未登录则显示 登录/注册 按钮）
    // const storeUser = useAuthStore((s) => s.auth?.user)
    const [fetchedUser, setFetchedUser] = useState<any | null>(null)
    const [loadingUser, setLoadingUser] = useState(false)

    useEffect(() => {
      ;(async () => {
        setLoadingUser(true)
        const token = readToken()
        // console.log('[NavUser] token raw:', token, 'type:', typeof token)
        if(!token) {
            setFetchedUser(null)
            setLoadingUser(false)
          return
        }
      //   if (!isJwtValid(token)) {
      //   // token 明显过期或损坏，清除本地并不请求后端
      //   useAuthStore.getState()?.auth?.resetAccessToken?.()
      //   if (mounted) {
      //     setFetchedUser(null)
      //     setLoadingUser(false)
      //   }
      //   return
      // }
        try {
          const resp = await apiGet('/api/users/profile')
          // 兼容后端直接返回 user 或 { user: ... }
          setFetchedUser(resp.data)
        } catch {
          setFetchedUser(null)
        } finally {
          setLoadingUser(false)
        }
      })()
      return () => {
      }
    }, [])

    // if (!storeUser) {
    //   return (
    //     <SidebarMenu>
    //       <SidebarMenuItem>
    //         <div className='w-full px-3 py-2'>
    //           <div className='flex gap-2 w-full'>
    //             {/* 两个按钮 flex-1 ，合起来占满侧栏条目宽度 */}
    //             <Link
    //               to='/sign-in-2'
    //               className='flex-1 text-base font-semibold text-center px-4 py-2 rounded-md border border-neutral-700 hover:opacity-90'
    //             >
    //               登录
    //             </Link>
    //             <Link
    //               to='/sign-up'
    //               className='flex-1 text-base font-semibold text-center px-4 py-2 rounded-md bg-primary text-primary-foreground hover:opacity-95'
    //             >
    //               注册
    //             </Link>
    //           </div>
    //         </div>
    //       </SidebarMenuItem>
    //     </SidebarMenu>
    //   )
    // }

    if (!fetchedUser) {
      const isCollapsed = state === 'collapsed'

      return (
        <SidebarMenu>
          <SidebarMenuItem>
            {/* SidebarMenuButton 自带尺寸/hover/tooltip 行为，asChild 用来包裹 Link */}
            <SidebarMenuButton
              asChild
              className='w-full'
              // tooltip 在侧栏折叠时会显示（TooltipContent 中已控制）
              tooltip='登录 / 注册'
              aria-label='登录或注册'
            >
              <Link
                to='/sign-in-2'
                className='w-full inline-flex items-center justify-start gap-3 text-sm font-semibold px-3 py-2 rounded-md border border-neutral-700 hover:opacity-90 h-10 leading-5 overflow-hidden'
              >
                <LogIn className='size-4' />
                {/* 折叠时隐藏文本，展开时展示；文本使用 truncate 防止换行 */}
                <span className={`${isCollapsed ? 'sr-only' : 'truncate'}`}>
                  登录 / 注册
                </span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      )
    }
    // 已登录：使用 storeUser 显示用户信息（忽略父组件传入的 sidebarData.user）
    const effectiveUser = fetchedUser

    // console.log('fetchedUser:', fetchedUser)

    // console.log('NavUser effectiveUser:', effectiveUser)

    const displayUserName =
      // 优先使用后端常见字段
      // (effectiveUser as any).full_name ??
      // (effectiveUser as any).name ??
      (effectiveUser as any).username ??
      // (effectiveUser as any).email ??
      'User'

    const displayName = (effectiveUser as any).full_name ?? displayUserName

    // console.log('displayName: ', displayName)

    const displayEmail = (effectiveUser as any).email ?? (effectiveUser as any).username ?? ''

    const avatarSrc = (effectiveUser as any).avatar_url ?? (effectiveUser as any).avatar ?? (effectiveUser as any).picture ?? ''

    const initials = getInitials(displayName)

    return (
      <>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  size='lg'
                  className='data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground'
                >
                  <Avatar className='h-8 w-8 rounded-lg'>
                    {avatarSrc ? (
                      <AvatarImage
                        src={buildStaticUrl(avatarSrc)}
                        alt={displayName}
                        crossOrigin="anonymous"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none'
                        }}
                      />
                    ) : (
                      <AvatarFallback className='rounded-lg'>{initials}</AvatarFallback>
                    )}
                  </Avatar>
                  <div className='grid flex-1 text-start text-sm leading-tight'>
                    <span className='truncate font-semibold'>{displayUserName}</span>
                    <span className='truncate text-xs'>{displayEmail}</span>
                  </div>
                  <ChevronsUpDown className='ms-auto size-4' />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className='w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg'
                side={isMobile ? 'bottom' : 'right'}
                align='end'
                sideOffset={4}
              >
                <DropdownMenuLabel className='p-0 font-normal'>
                  <div className='flex items-center gap-2 px-1 py-1.5 text-start text-sm'>
                    <Avatar className='h-8 w-8 rounded-lg'>
                      {avatarSrc ? (
                        <AvatarImage
                          src={buildStaticUrl(avatarSrc)}
                          alt={displayName}
                          crossOrigin="anonymous"
                        />
                      ) : (
                        <AvatarFallback className='rounded-lg'>{initials}</AvatarFallback>
                      )}
                    </Avatar>
                    <div className='grid flex-1 text-start text-sm leading-tight'>
                      <span className='truncate font-semibold'>{displayUserName}</span>
                      <span className='truncate text-xs'>{displayEmail}</span>
                    </div>
                  </div>
                </DropdownMenuLabel>
                {/* <DropdownMenuSeparator /> */}
                  <DropdownMenuGroup>
                  {/* <DropdownMenuItem>
                    <MessageSquare />
                    Upgrade to Pro
                  </DropdownMenuItem> */}
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                  <DropdownMenuItem asChild>
                    <Link to='/settings'>
                      <BadgeCheck />
                      账户
                    </Link>
                  </DropdownMenuItem>
                  {/* <DropdownMenuItem asChild>
                    <Link to='/settings'>
                      <CreditCard />
                      Billing
                    </Link>
                  </DropdownMenuItem> */}
                  <DropdownMenuItem asChild>
                    <Link to='/settings/notifications'>
                      <Bell />
                      通知
                    </Link>
                  </DropdownMenuItem>
                  {(() => {
                    const roles = Array.isArray(effectiveUser?.role)
                      ? effectiveUser.role
                      : effectiveUser?.role
                      ? [effectiveUser.role]
                      : []
                    if (roles.includes('user')) {
                      return (
                        <DropdownMenuItem onClick={() => feedback.setOpen('create')}>
                          <MessageSquare />
                          提交反馈
                        </DropdownMenuItem>
                      )
                    }
                    return null
                  })()}
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  variant='destructive'
                  onClick={() => setOpen(true)}
                >
                  <LogOut />
                  登出
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>

        <SignOutDialog open={!!open} onOpenChange={setOpen} />
      </>
    )
  }
