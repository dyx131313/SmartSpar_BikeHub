import { createFileRoute } from '@tanstack/react-router'
import { HelpCenter } from '@/features/help_center'

export const Route = createFileRoute('/_authenticated/help-center/')({
  component: HelpCenter,
})
