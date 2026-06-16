import { z } from 'zod'
import { createFileRoute, redirect } from '@tanstack/react-router'

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

export const Route = createFileRoute('/_authenticated/demand_management/')({
  validateSearch: demandSearchSchema,
  beforeLoad: ({ search }) => {
    throw redirect({
      to: '/demand-management',
      search,
    })
  },
})
