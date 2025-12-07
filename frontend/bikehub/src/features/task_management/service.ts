import { apiGet, apiPost, apiPut, apiDelete } from '@/lib/api'
import { Task } from './data/schema'

export interface TaskListResponse {
    data: Task[]
    total: number
    pages: number
    current_page: number
    per_page: number
}

export const getTasks = async (params?: { page?: number; per_page?: number; status?: string; priority?: number; assigned_to?: number }) => {
    const queryString = params ? '?' + new URLSearchParams(params as any).toString() : ''
    return apiGet(`/api/dispatch-tasks${queryString}`) as Promise<TaskListResponse>
}

export const createTask = async (data: Partial<Task>) => {
    return apiPost('/api/dispatch-tasks', data)
}

export const updateTask = async (id: number, data: Partial<Task>) => {
    return apiPut(`/api/dispatch-tasks/${id}`, data)
}

export const deleteTask = async (id: number) => {
    return apiDelete(`/api/dispatch-tasks/${id}`)
}

export const getTask = async (id: number) => {
    return apiGet(`/api/dispatch-tasks/${id}`) as Promise<{ data: Task }>
}

export const getRouteForTask = async (taskId: number) => {
    return apiGet(`/api/route-planning/task/${taskId}`) as Promise<{ data: any }>
}