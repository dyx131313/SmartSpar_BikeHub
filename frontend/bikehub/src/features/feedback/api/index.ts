import { apiGet, apiPost, apiPut } from '@/lib/api'

export interface Feedback {
  id: number
  user_id: number
  user?: {
    id: number
    username: string
    full_name: string
  }
  category: 'user_feedback' | 'dispatcher_issue'
  category_display: string
  title: string
  content: string
  status: 'pending' | 'processing' | 'resolved' | 'closed'
  status_display: string
  created_at: string
  updated_at: string
  resolution_notes?: string
  resolved_by?: number
  resolver?: {
    id: number
    username: string
    full_name: string
  }
  resolved_at?: string
}

export interface FeedbackListResponse {
  data: Feedback[]
  total: number
  pages: number
  current_page: number
  per_page: number
}

export interface CreateFeedbackData {
  title: string
  content: string
  category?: 'user_feedback' | 'dispatcher_issue'
}

export interface UpdateFeedbackData {
  status?: 'pending' | 'processing' | 'resolved' | 'closed'
  resolution_notes?: string
}

export const getFeedbacks = async (params: {
  page?: number
  per_page?: number
  status?: string
  category?: string
}) => {
  const queryString = new URLSearchParams()
  if (params.page) queryString.append('page', params.page.toString())
  if (params.per_page) queryString.append('per_page', params.per_page.toString())
  if (params.status) queryString.append('status', params.status)
  if (params.category) queryString.append('category', params.category)
  
  return apiGet(`/api/feedback?${queryString.toString()}`) as Promise<FeedbackListResponse>
}

export const createFeedback = async (data: CreateFeedbackData) => {
  return apiPost('/api/feedback', data)
}

export const updateFeedback = async (id: number, data: UpdateFeedbackData) => {
  return apiPut(`/api/feedback/${id}`, data)
}



