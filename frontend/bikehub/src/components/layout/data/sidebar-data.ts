import { BarChart2, Command, HelpCircle, ListTodo, MapPin, MessagesSquare, Settings, TrendingUp, UserCog, Users } from 'lucide-react'
import { type SidebarData } from '../types'

export const sidebarData: SidebarData = {
  user: {
    name: 'BikeHub',
    email: 'operations@bikehub.local',
    avatar: '/images/logo_design.svg',
  },
  teams: [
    {
      name: 'SmartSpar_BikeHub',
      logo: Command,
      plan: '运营调度平台',
    },
  ],
  navGroups: [
    {
      title: '控制面板',
      items: [
        {
          title: '数据展示面板',
          url: '/',
          icon: BarChart2,
          roles: ['admin', 'dispatcher'],
        },        
        {
          title: '站点管理',
          url: '/station_management',
          icon: MapPin,
          roles: ['admin', 'dispatcher'],
        },
        {
          title: '调度管理',
          url: '/task_management',
          icon: ListTodo,
          roles: ['admin', 'dispatcher', 'operator'],
        },
        {
          title: '需求数据管理',
          url: '/demand-management',
          icon: TrendingUp,
          roles: ['admin', 'dispatcher'],
        },
        // {
        //   title: 'Apps',
        //   url: '/apps',
        //   icon: Package,
        // },
        {
          title: '用户管理',
          url: '/users',
          icon: Users,
          roles: ['admin'],
        },
        {
          title: '反馈管理',
          url: '/feedback',
          icon: MessagesSquare,
          roles: ['admin', 'dispatcher'],
        },

        // {
        //   title: 'Secured by Clerk',
        //   icon: ClerkLogo,
        //   items: [
        //     {
        //       title: 'Sign In',
        //       url: '/clerk/sign-in',
        //     },
        //     {
        //       title: 'Sign Up',
        //       url: '/clerk/sign-up',
        //     },
        //     {
        //       title: 'User Management',
        //       url: '/clerk/user-management',
        //     },
        //   ],
        // },
      ],
    },
    {
      title: "个人",
      items: [
        {
          title: '群聊',
          url: '/chat/groups',
          // badge: '3',
          icon: MessagesSquare,
        },
        {
          title: '设置',
          icon: Settings,
          items: [
            {
              title: '个人资料',
              url: '/settings',
              icon: UserCog,
            },
            // {
            //   title: '账户',
            //   url: '/settings/account',
            //   icon: Wrench,
            // },
            // {
            //   title: '外观',
            //   url: '/settings/appearance',
            //   icon: Palette,
            // },
            // {
            //   title: '通知',
            //   url: '/settings/notifications',
            //   icon: Bell,
            // },
              // {
              //   title: '显示',
              //   url: '/settings/display',
              //   icon: Monitor,
              // },
          ],
        },
      ],
    },
    // {
    //   title: 'Pages',
    //   items: [
    //     {
    //       title: 'Auth',
    //       icon: ShieldCheck,
    //       items: [
    //         // {
    //         //   title: 'Sign In',
    //         //   url: '/sign-in',
    //         // },
    //         {
    //           title: '登录',
    //           url: '/sign-in-2',
    //         },
    //         {
    //           title: '注册',
    //           url: '/sign-up',
    //         },
    //         {
    //           title: '忘记密码',
    //           url: '/forgot-password',
    //         },
    //         {
    //           title: 'OTP',
    //           url: '/otp',
    //         },
    //       ],
    //     },
        // {
        //   title: 'Errors',
        //   icon: Bug,
        //   items: [
        //     {
        //       title: 'Unauthorized',
        //       url: '/errors/unauthorized',
        //       icon: Lock,
        //     },
        //     {
        //       title: 'Forbidden',
        //       url: '/errors/forbidden',
        //       icon: UserX,
        //     },
        //     {
        //       title: 'Not Found',
        //       url: '/errors/not-found',
        //       icon: FileX,
        //     },
        //     {
        //       title: 'Internal Server Error',
        //       url: '/errors/internal-server-error',
        //       icon: ServerOff,
        //     },
        //     {
        //       title: 'Maintenance Error',
        //       url: '/errors/maintenance-error',
        //       icon: Construction,
        //     },
        //   ],
        // },
      // ],
    // },
    {
      title: '其他',
      items: [
        
        {
          title: '帮助中心',
          url: '/help-center',
          icon: HelpCircle,
        },
      ],
    },
  ],
}
