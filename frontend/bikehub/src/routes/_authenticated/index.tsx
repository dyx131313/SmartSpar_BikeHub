import { createFileRoute } from '@tanstack/react-router'
import { Dashboard } from '@/features/dashboard/index'

export const Route = createFileRoute('/_authenticated/')({
  component: Dashboard,
})
