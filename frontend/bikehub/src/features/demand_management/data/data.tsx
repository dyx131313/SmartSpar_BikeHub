import {
  Cloud,
  CloudRain,
  Sun,
  CloudLightning,
  Snowflake,
  Building2,
  Home,
  Briefcase,
  School,
  ShoppingBag,
} from 'lucide-react'

export const stationTypes = [
  // {
  //   label: '商业区',
  //   value: 'commercial',
  //   icon: Briefcase,
  // },
  // {
  //   label: '住宅区',
  //   value: 'residential',
  //   icon: Home,
  // },
  // {
  //   label: '学校',
  //   value: 'school',
  //   icon: School,
  // },
  // {
  //   label: '工业区',
  //   value: 'industrial',
  //   icon: Building2,
  // },
  // {
  //   label: '购物中心',
  //   value: 'shopping',
  //   icon: ShoppingBag,
  // },
  // 常见后台值的中文映射，保证预测视图能正确展示中文
  {
    label: '食堂',
    value: 'canteen',
    icon: Building2,
  },
  {
    label: '教学楼',
    value: 'teaching_building',
    icon: School,
  },
  {
    label: '图书馆',
    value: 'library',
    icon: School,
  },
  {
    label: '宿舍',
    value: 'dormitory',
    icon: Home,
  },
  {
    label: '其他',
    value: 'other',
    icon: Briefcase,
  },
]

export const weatherTypes = [
  // {
  //   label: '晴朗',
  //   value: 'sunny',
  //   icon: Sun,
  // },
  // {
  //   label: '多云',
  //   value: 'cloudy',
  //   icon: Cloud,
  // },
  // {
  //   label: '雨天',
  //   value: 'rainy',
  //   icon: CloudRain,
  // },
  // {
  //   label: '雷雨',
  //   value: 'stormy',
  //   icon: CloudLightning,
  // },
  // {
  //   label: '雪天',
  //   value: 'snowy',
  //   icon: Snowflake,
  // },
  // 兼容后端可能使用的其他英文或中文表示
  { label: '晴天', value: '晴', icon: Sun },
  { label: '多云', value: '多云', icon: Cloud },
  // { label: '雨天', value: 'rain', icon: CloudRain },
  { label: '雨天', value: '雨', icon: CloudRain },
  // { label: '雷雨', value: 'storm', icon: CloudLightning },
  // { label: '雪天', value: 'snow', icon: Snowflake },
  { label: '雪天', value: '雪', icon: Snowflake },
  { label: '阴天', value: '阴', icon: Cloud}
]
