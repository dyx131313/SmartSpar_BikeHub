import { createFileRoute } from '@tanstack/react-router'
import { GroupChats } from '@/features/chats'

export const Route = createFileRoute('/_authenticated/chats/group')({
  component: GroupChats,
})