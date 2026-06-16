import {
  ThemeSettingsPanel,
  ThemeSettingsResetButton,
} from '@/components/config-drawer'
import { ContentSection } from '../components/content-section'

export function SettingsAppearance() {
  return (
    <ContentSection
      title='外观与布局'
      desc='集中管理主题、侧边栏、页面布局和阅读方向。'
    >
      <div className='space-y-8'>
        <ThemeSettingsPanel />
        <div className='border-border/70 flex justify-end border-t pt-6'>
          <ThemeSettingsResetButton />
        </div>
      </div>
    </ContentSection>
  )
}
