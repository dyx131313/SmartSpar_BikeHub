import { z } from 'zod'
import { createFileRoute } from '@tanstack/react-router'
import { DemandManagement } from '@/features/demand_management'
import { RequireRole } from '@/components/require-role'

const demandSearchSchema = z.object({
  page: z.number().optional().catch(1),
  pageSize: z.number().optional().catch(10),
  station_type: z
    .array(z.string())
    .optional()
    .catch([]),
  weather: z
    .array(z.string())
    .optional()
    .catch([]),
  filter: z.string().optional().catch(''),
})

// Force update
export const Route = createFileRoute('/_authenticated/demand_management/')({
  component: () => (
    <RequireRole roles={['admin', 'dispatcher', 'operator']}>
      <DemandManagement />
    </RequireRole>
  ),
})
