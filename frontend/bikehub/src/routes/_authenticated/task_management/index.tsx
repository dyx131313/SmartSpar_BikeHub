import z from 'zod'
import { createFileRoute } from '@tanstack/react-router'
import { Tasks } from '@/features/task_management'
import { priorities, statuses } from '@/features/task_management/data/data'

const taskSearchSchema = z.object({
  page: z.number().optional().catch(1),
  pageSize: z.number().optional().catch(10),
  status: z
    .array(z.string())
    .optional()
    .catch([]),
  priority: z
    .array(z.string())
    .optional()
    .catch([]),
  filter: z.string().optional().catch(''),
})

import { RequireRole } from '@/components/require-role'

export const Route = createFileRoute('/_authenticated/task_management/')({
  validateSearch: taskSearchSchema,
  component: () => (
    <RequireRole roles={['admin', 'dispatcher', 'operator']}>
      <Tasks />
    </RequireRole>
  ),
})
