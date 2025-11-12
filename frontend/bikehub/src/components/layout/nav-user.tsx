// import { Link } from '@tanstack/react-router'
// import {
//   BadgeCheck,
//   Bell,
//   ChevronsUpDown,
//   CreditCard,
//   LogOut,
//   Sparkles,
// } from 'lucide-react'
// import useDialogState from '@/hooks/use-dialog-state'
// import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
// import {
//   DropdownMenu,
//   DropdownMenuContent,
//   DropdownMenuGroup,
//   DropdownMenuItem,
//   DropdownMenuLabel,
//   DropdownMenuSeparator,
//   DropdownMenuTrigger,
// } from '@/components/ui/dropdown-menu'
// import {
//   SidebarMenu,
//   SidebarMenuButton,
//   SidebarMenuItem,
//   useSidebar,
// } from '@/components/ui/sidebar'
// import { SignOutDialog } from '@/components/sign-out-dialog'

// type NavUserProps = {
//   user: {
//     name: string
//     email: string
//     avatar: string
//   }
// }

// export function NavUser({ user }: NavUserProps) {
//   const { isMobile } = useSidebar()
//   const [open, setOpen] = useDialogState()

//   return (
//     <>
//       <SidebarMenu>
//         <SidebarMenuItem>
//           <DropdownMenu>
//             <DropdownMenuTrigger asChild>
//               <SidebarMenuButton
//                 size='lg'
//                 className='data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground'
//               >
//                 <Avatar className='h-8 w-8 rounded-lg'>
//                   <AvatarImage src={user.avatar} alt={user.name} />
//                   <AvatarFallback className='rounded-lg'>SN</AvatarFallback>
//                 </Avatar>
//                 <div className='grid flex-1 text-start text-sm leading-tight'>
//                   <span className='truncate font-semibold'>{user.name}</span>
//                   <span className='truncate text-xs'>{user.email}</span>
//                 </div>
//                 <ChevronsUpDown className='ms-auto size-4' />
//               </SidebarMenuButton>
//             </DropdownMenuTrigger>
//             <DropdownMenuContent
//               className='w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg'
//               side={isMobile ? 'bottom' : 'right'}
//               align='end'
//               sideOffset={4}
//             >
//               <DropdownMenuLabel className='p-0 font-normal'>
//                 <div className='flex items-center gap-2 px-1 py-1.5 text-start text-sm'>
//                   <Avatar className='h-8 w-8 rounded-lg'>
//                     <AvatarImage src={user.avatar} alt={user.name} />
//                     <AvatarFallback className='rounded-lg'>SN</AvatarFallback>
//                   </Avatar>
//                   <div className='grid flex-1 text-start text-sm leading-tight'>
//                     <span className='truncate font-semibold'>{user.name}</span>
//                     <span className='truncate text-xs'>{user.email}</span>
//                   </div>
//                 </div>
//               </DropdownMenuLabel>
//               <DropdownMenuSeparator />
//               <DropdownMenuGroup>
//                 <DropdownMenuItem>
//                   <Sparkles />
//                   Upgrade to Pro
//                 </DropdownMenuItem>
//               </DropdownMenuGroup>
//               <DropdownMenuSeparator />
//               <DropdownMenuGroup>
//                 <DropdownMenuItem asChild>
//                   <Link to='/settings/account'>
//                     <BadgeCheck />
//                     Account
//                   </Link>
//                 </DropdownMenuItem>
//                 <DropdownMenuItem asChild>
//                   <Link to='/settings'>
//                     <CreditCard />
//                     Billing
//                   </Link>
//                 </DropdownMenuItem>
//                 <DropdownMenuItem asChild>
//                   <Link to='/settings/notifications'>
//                     <Bell />
//                     Notifications
//                   </Link>
//                 </DropdownMenuItem>
//               </DropdownMenuGroup>
//               <DropdownMenuSeparator />
//               <DropdownMenuItem
//                 variant='destructive'
//                 onClick={() => setOpen(true)}
//               >
//                 <LogOut />
//                 Sign out
//               </DropdownMenuItem>
//             </DropdownMenuContent>
//           </DropdownMenu>
//         </SidebarMenuItem>
//       </SidebarMenu>

//       <SignOutDialog open={!!open} onOpenChange={setOpen} />
//     </>
//   )
// }


import { Link } from '@tanstack/react-router'
import {
  BadgeCheck,
  Bell,
  ChevronsUpDown,
  CreditCard,
  LogOut,
  Sparkles,
} from 'lucide-react'
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

type NavUserProps = {
  user?: {
    name?: string
    email?: string
    avatar?: string
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

export function NavUser({ user }: NavUserProps) {
  const { isMobile } = useSidebar()
  const [open, setOpen] = useDialogState()


  // 从全局 store 读取 user（优先 props）
  const storeUser = useAuthStore((s) => s.auth?.user)
  const effectiveUser = storeUser ?? user ?? {}

  // console.log('NavUser effectiveUser:', effectiveUser)

  const displayName =
    // 优先使用后端常见字段
    (effectiveUser as any).full_name ??
    (effectiveUser as any).name ??
    (effectiveUser as any).username ??
    (effectiveUser as any).email ??
    'User'

  const displayEmail = (effectiveUser as any).email ?? (effectiveUser as any).username ?? ''

  const avatarSrc = (effectiveUser as any).avatar ?? (effectiveUser as any).picture ?? ''

  const initials = getInitials(displayName)

  // console.log(displayName, displayEmail, avatarSrc, initials)

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
                    <AvatarImage src={avatarSrc} alt={displayName} />
                  ) : (
                    <AvatarFallback className='rounded-lg'>{initials}</AvatarFallback>
                  )}
                </Avatar>
                <div className='grid flex-1 text-start text-sm leading-tight'>
                  <span className='truncate font-semibold'>{displayName}</span>
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
                      <AvatarImage src={avatarSrc} alt={displayName} />
                    ) : (
                      <AvatarFallback className='rounded-lg'>{initials}</AvatarFallback>
                    )}
                  </Avatar>
                  <div className='grid flex-1 text-start text-sm leading-tight'>
                    <span className='truncate font-semibold'>{displayName}</span>
                    <span className='truncate text-xs'>{displayEmail}</span>
                  </div>
                </div>
              </DropdownMenuLabel>
              {/* <DropdownMenuSeparator /> */}
              <DropdownMenuGroup>
                {/* <DropdownMenuItem>
                  <Sparkles />
                  Upgrade to Pro
                </DropdownMenuItem> */}
              </DropdownMenuGroup>
              <DropdownMenuSeparator />
              <DropdownMenuGroup>
                <DropdownMenuItem asChild>
                  <Link to='/settings/account'>
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