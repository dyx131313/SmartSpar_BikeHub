import { z } from 'zod'

const userRoleSchema = z.string()

export const userSchema = z.object({
  id: z.number(),
  username: z.string(),
  email: z.string(),
  role: userRoleSchema,
  full_name: z.string().nullish(),
  phone: z.string().nullish(),
  is_active: z.boolean(),
  last_login: z.string().nullish(),
  created_at: z.string().nullish(),
  updated_at: z.string().nullish(),
})

export type User = z.infer<typeof userSchema>

export const userListSchema = z.array(userSchema)
