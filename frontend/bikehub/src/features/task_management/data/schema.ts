import { z } from 'zod'

// We're keeping a simple non-relational schema here.
// IRL, you will have a schema for your data models.
export const taskSchema = z.object({
  id: z.number(),
  task_name: z.string(),
  from_station_id: z.number().nullish(),
  to_station_id: z.number().nullish(),
  bike_count: z.number(),
  priority: z.number(),
  status: z.string(),
  assigned_to: z.number().nullish(),
  created_by: z.number(),
  created_at: z.string().nullish(),
  updated_at: z.string().nullish(),
})

export type Task = z.infer<typeof taskSchema>
