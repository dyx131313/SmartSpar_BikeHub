import { z } from 'zod'

// We're keeping a simple non-relational schema here.
// IRL, you will have a schema for your data models.
export const taskSchema = z.object({
  id: z.string(),
  // title: z.string(),
  from_station_id: z.number(),
  to_station_id: z.number(),
  bike_count: z.number(),
  priority: z.string(),
  status: z.string(),
  assignee_id: z.number(),
  creator_id: z.number(),
  // label: z.string(),
})

export type Task = z.infer<typeof taskSchema>
