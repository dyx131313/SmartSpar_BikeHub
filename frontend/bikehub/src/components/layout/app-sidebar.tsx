import { useLayout } from '@/context/layout-provider'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from '@/components/ui/sidebar'
// import { AppTitle } from './app-title'
import { sidebarData } from './data/sidebar-data'
import { NavGroup } from './nav-group'
import { NavUser } from './nav-user'
import { TeamSwitcher } from './team-switcher'
import { useAuthStore } from '@/stores/auth-store'

export function AppSidebar() {
  const { collapsible, variant } = useLayout()
  const user = useAuthStore((s) => s.auth?.user)

  const filteredNavGroups = sidebarData.navGroups.map((group) => {
    const filteredItems = group.items.filter((item) => {
      if (!item.roles || item.roles.length === 0) return true
      if (!user) return false
      const userRoles = Array.isArray(user.role) ? user.role : [user.role]
      return item.roles.some((r) => userRoles.includes(r))
    })
    return { ...group, items: filteredItems }
  })

  return (
    <Sidebar collapsible={collapsible} variant={variant}>
      <SidebarHeader>
        <NavUser/>


        {/* Replace <TeamSwitch /> with the following <AppTitle />
         /* if you want to use the normal app title instead of TeamSwitch dropdown */}
        {/* <AppTitle /> */}
      </SidebarHeader>
      <SidebarContent>
        {filteredNavGroups.map((props) => (
          <NavGroup key={props.title} {...props} />
        ))}
      </SidebarContent>
      <SidebarFooter>
        {/* <TeamSwitcher teams={sidebarData.teams} /> */}
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
