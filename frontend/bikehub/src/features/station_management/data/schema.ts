import { z } from 'zod'

// We're keeping a simple non-relational schema here.
// IRL, you will have a schema for your data models.
export const stationSchema = z.object({
  id: z.string(),
  title: z.string(),
  // fuck_me: z.string(),
  name: z.string(),
  station_type: z.string(),
  latitude: z.number(),
  longitude: z.number(),
  capacity: z.number(),
  description: z.string(),
  status: z.string(),
  label: z.string(),
  priority: z.string(),
})

export type Station = z.infer<typeof stationSchema>
