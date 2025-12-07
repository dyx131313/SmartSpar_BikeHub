import { createFileRoute } from '@tanstack/react-router'
import { GroupChats } from '@/features/chat'

export const Route = createFileRoute('/_authenticated/chat/groups')({
  component: GroupChats,
})