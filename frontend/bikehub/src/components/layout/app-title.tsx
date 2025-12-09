import { Link } from '@tanstack/react-router'
import { Menu, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar'
import { Button } from '../ui/button'

export function AppTitle() {
  const { setOpenMobile } = useSidebar()
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton
          size='lg'
          className='gap-2 py-2 hover:bg-transparent active:bg-transparent'
          asChild
        >
          <div className='flex items-center gap-2 w-full'>
            <Link
              to='/'
              onClick={() => setOpenMobile(false)}
              className='flex items-center gap-2 flex-1 min-w-0'
            >
              <img
                src='/images/logo_design.png'
                alt='SmartSpar BikeHub Logo'
                className='h-12 w-12 flex-shrink-0 object-contain'
              />
              <div className='flex flex-col text-start min-w-0'>
                <span className='truncate font-bold text-sm leading-tight'>SmartSpar BikeHub</span>
                <span className='truncate text-xs text-muted-foreground'>智慧共享单车调度系统</span>
              </div>
            </Link>
            <ToggleSidebar />
          </div>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}

function ToggleSidebar({
  className,
  onClick,
  ...props
}: React.ComponentProps<typeof Button>) {
  const { toggleSidebar } = useSidebar()

  return (
    <Button
      data-sidebar='trigger'
      data-slot='sidebar-trigger'
      variant='ghost'
      size='icon'
      className={cn('aspect-square size-8 max-md:scale-125', className)}
      onClick={(event) => {
        onClick?.(event)
        toggleSidebar()
      }}
      {...props}
    >
      <X className='md:hidden' />
      <Menu className='max-md:hidden' />
      <span className='sr-only'>Toggle Sidebar</span>
    </Button>
  )
}
