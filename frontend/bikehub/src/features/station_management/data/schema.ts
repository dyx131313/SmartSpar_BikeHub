import { z } from 'zod'

// We're keeping a simple non-relational schema here.
// IRL, you will have a schema for your data models.
export const stationSchema = z.object({
  id: z.number(),
  name: z.string(),
  station_type: z.string(),
  latitude: z.number(),
  longitude: z.number(),
  capacity: z.number(),
  description: z.string(),
  created_at: z.string().nullish(),
  updated_at: z.string().nullish(),
})

export type Station = z.infer<typeof stationSchema>

export interface StationDashboardData extends Station {
  current_bikes: number
  predicted_demand: number
  real_demand: number
}
