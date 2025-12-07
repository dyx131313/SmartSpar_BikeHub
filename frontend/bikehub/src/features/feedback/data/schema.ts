import { z } from 'zod'

export const feedbackSchema = z.object({
  id: z.number(),
  user_id: z.number(),
  user: z.object({
    id: z.number(),
    username: z.string(),
    full_name: z.string(),
  }).optional(),
  category: z.enum(['user_feedback', 'dispatcher_issue']),
  category_display: z.string(),
  title: z.string(),
  content: z.string(),
  status: z.enum(['pending', 'processing', 'resolved', 'closed']),
  status_display: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  resolution_notes: z.string().optional(),
  resolved_by: z.number().optional(),
  resolver: z.object({
    id: z.number(),
    username: z.string(),
    full_name: z.string(),
  }).optional(),
  resolved_at: z.string().optional(),
})

export type Feedback = z.infer<typeof feedbackSchema>



