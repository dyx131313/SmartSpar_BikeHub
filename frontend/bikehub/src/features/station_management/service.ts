import { apiGet, apiPost, apiPut, apiDelete } from '@/lib/api'
import { Station, StationDashboardData } from './data/schema'

// 定义后端返回的列表结构
export interface StationListResponse {
    data: Station[]
    total: number
    pages: number
    current_page: number
    per_page: number
}

export interface DashboardStationsResponse {
    data: StationDashboardData[]
    count: number
}

// 获取仪表盘聚合数据
export const getDashboardStations = async () => {
    return apiGet('/api/dashboard/stations') as Promise<DashboardStationsResponse>
}

// 获取站点列表
export const getStations = async (params?: { page?: number; per_page?: number; station_type?: string }) => {
    const queryString = params ? '?' + new URLSearchParams(params as any).toString() : ''
    return apiGet(`/api/stations${queryString}`) as Promise<StationListResponse>
}

// 获取单个站点
export const getStation = async (id: number) => {
    return apiGet(`/api/stations/${id}`) as Promise<{ data: Station }>
}

// 创建站点
export const createStation = async (data: Omit<Station, 'id' | 'created_at' | 'updated_at'>) => {
    return apiPost('/api/stations', data)
}

// 更新站点
export const updateStation = async (id: number, data: Partial<Omit<Station, 'id' | 'created_at' | 'updated_at'>>) => {
    return apiPut(`/api/stations/${id}`, data)
}

// 删除站点
export const deleteStation = async (id: number) => {
    // apiDelete 需要在 lib/api.ts 中实现，或者直接用 fetchWithAuth
    // 暂时假设 apiDelete 存在，如果不存在我需要去添加
    // 检查 lib/api.ts 发现没有 apiDelete，我需要先去添加 apiDelete 或者直接在这里实现
    // 为了保持一致性，我应该先去 lib/api.ts 添加 apiDelete
    // 但为了不打断流程，我先用 apiPost 模拟或者直接在这里写 fetch
    // 还是先去 lib/api.ts 添加 apiDelete 比较好
    return apiDelete(`/api/stations/${id}`)
}
