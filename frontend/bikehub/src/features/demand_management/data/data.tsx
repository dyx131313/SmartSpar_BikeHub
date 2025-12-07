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
  {
    label: '商业区',
    value: 'commercial',
    icon: Briefcase,
  },
  {
    label: '住宅区',
    value: 'residential',
    icon: Home,
  },
  {
    label: '学校',
    value: 'school',
    icon: School,
  },
  {
    label: '工业区',
    value: 'industrial',
    icon: Building2,
  },
  {
    label: '购物中心',
    value: 'shopping',
    icon: ShoppingBag,
  },
]

export const weatherTypes = [
  {
    label: '晴朗',
    value: 'sunny',
    icon: Sun,
  },
  {
    label: '多云',
    value: 'cloudy',
    icon: Cloud,
  },
  {
    label: '雨天',
    value: 'rainy',
    icon: CloudRain,
  },
  {
    label: '雷雨',
    value: 'stormy',
    icon: CloudLightning,
  },
  {
    label: '雪天',
    value: 'snowy',
    icon: Snowflake,
  },
]
