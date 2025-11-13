import { ContentSection } from '../components/content-section'
import { DisplayForm } from './display-form'

export function SettingsDisplay() {
  return (
    <ContentSection
      title='显示设置'
      desc="打开或关闭项目以控制应用程序中显示的内容。"
    >
      <DisplayForm />
    </ContentSection>
  )
}
