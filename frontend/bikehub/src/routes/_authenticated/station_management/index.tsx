import z from 'zod'
import { createFileRoute } from '@tanstack/react-router'
import { Management } from '@/features/station_management'
import { priorities, statuses } from '@/features/station_management/data/data'

const taskSearchSchema = z.object({
  page: z.number().optional().catch(1),
  pageSize: z.number().optional().catch(10),
  status: z
    .array(z.enum(statuses.map((status) => status.value)))
    .optional()
    .catch([]),
  priority: z
    .array(z.enum(priorities.map((priority) => priority.value)))
    .optional()
    .catch([]),
  filter: z.string().optional().catch(''),
})

import { RequireRole } from '@/components/require-role'

export const Route = createFileRoute('/_authenticated/station_management/')({
  validateSearch: taskSearchSchema,
  component: () => (
    <RequireRole roles={['admin', 'dispatcher', 'operator']}>
      <Management />
    </RequireRole>
  ),
})
