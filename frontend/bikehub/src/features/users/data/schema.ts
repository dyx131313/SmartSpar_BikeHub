import { z } from 'zod'

const userStatusSchema = z.union([
  z.literal('已激活'),
  z.literal('未激活'),
  // z.literal('已邀请'),
  z.literal('被暂停'),
])
export type UserStatus = z.infer<typeof userStatusSchema>

const userRoleSchema = z.union([
  z.literal('superadmin'),
  z.literal('admin'),
  z.literal('dispatcher'),
])

const userSchema = z.object({
  id: z.string(),
  username: z.string(),
  email: z.string(),
  role: userRoleSchema,
  firstName: z.string(),
  lastName: z.string(),
  phoneNumber: z.string(),
  status: userStatusSchema,
  last_login: z.coerce.date().nullable(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
})
export type User = z.infer<typeof userSchema>

export const userListSchema = z.array(userSchema)
