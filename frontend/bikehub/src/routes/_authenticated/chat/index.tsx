import { createFileRoute } from '@tanstack/react-router'
import { Chats } from '@/features/chat'

export const Route = createFileRoute('/_authenticated/chat/')({
  component: Chats,
})
