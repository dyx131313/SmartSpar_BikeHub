import { z } from 'zod'

export const demandSchema = z.object({
  id: z.number(),
  timestamp: z.string(),
  station_id: z.number(),
  station_name: z.string().optional(),
  station_type: z.string(),
  weekday: z.number(),
  is_holiday: z.boolean(),
  weather: z.string(),
  temp: z.number(),
  demand: z.number(),
  created_at: z.string().nullish(),
})

export type Demand = z.infer<typeof demandSchema>
