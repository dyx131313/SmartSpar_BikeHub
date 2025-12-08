import { apiGet, apiPost, apiPut, apiDelete } from '@/lib/api'
import { User } from './data/schema'

export interface UserListResponse {
    data: User[]
    total: number
    pages: number
    current_page: number
    per_page: number
}

export const getUsers = async (params?: { page?: number; per_page?: number; role?: string }) => {
    const queryString = params ? '?' + new URLSearchParams(params as any).toString() : ''
    return apiGet(`/api/users${queryString}`) as Promise<UserListResponse>
}

export const createUser = async (data: Partial<User> & { password?: string }) => {
    return apiPost('/api/users', data)
}

export const updateUser = async (id: number, data: Partial<User> & { password?: string }) => {
    return apiPut(`/api/users/${id}`, data)
}

export const deleteUser = async (id: number) => {
    return apiDelete(`/api/users/${id}`)
}

export const getUser = async (id: number) => {
    return apiGet(`/api/users/${id}`) as Promise<{ data: User }>
}
