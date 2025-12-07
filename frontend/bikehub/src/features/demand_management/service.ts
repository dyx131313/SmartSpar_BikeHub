import { apiGet, apiPost, apiPut, apiDelete, apiUpload } from '@/lib/api'
import { Demand } from './data/schema'

export interface DemandListResponse {
    data: Demand[]
    total: number
    pages: number
    current_page: number
    per_page: number
}

export const getDemands = async (params?: { page?: number; per_page?: number; station_type?: string; weather?: string }) => {
    const queryString = params ? '?' + new URLSearchParams(params as any).toString() : ''
    return apiGet(`/api/demand-data${queryString}`) as Promise<DemandListResponse>
}

export const createDemand = async (data: Partial<Demand>) => {
    return apiPost('/api/demand-data', data)
}

export const updateDemand = async (id: number, data: Partial<Demand>) => {
    return apiPut(`/api/demand-data/${id}`, data)
}

export const deleteDemand = async (id: number) => {
    return apiDelete(`/api/demand-data/${id}`)
}

export const getDemand = async (id: number) => {
    return apiGet(`/api/demand-data/${id}`) as Promise<{ data: Demand }>
}

export const importDemands = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiUpload('/api/demand-data/import', formData)
}
