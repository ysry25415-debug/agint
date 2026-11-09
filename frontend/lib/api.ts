/**
 * API client for Product Hunter AI
 * Handles communication with the backend API
 */

import axios, { AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.warn('Unauthorized access')
    }

    if (error.response?.status === 403) {
      // Handle forbidden
      console.warn('Forbidden access')
    }

    return Promise.reject(error)
  }
)

// Generic fetcher function for React Query
export async function fetcher<T>(url: string): Promise<T> {
  const response = await api.get<T>(url)
  return response.data
}

// POST function
export async function post<T>(url: string, data: any): Promise<T> {
  const response = await api.post<T>(url, data)
  return response.data
}

// PUT function
export async function put<T>(url: string, data: any): Promise<T> {
  const response = await api.put<T>(url, data)
  return response.data
}

// DELETE function
export async function del<T>(url: string): Promise<T> {
  const response = await api.delete<T>(url)
  return response.data
}

// Types for API responses
export interface APIResponse<T> {
  success: boolean
  message: string
  data?: T
  errors?: string[]
}

export interface Product {
  id: number
  normalized_name: string
  brand: string | null
  model_number: string | null
  category: string
  description: string | null
  image_url: string | null
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface Source {
  id: number
  name: string
  type: string
  country_focus: string | null
  is_active: boolean
  status: string
  error_message: string | null
  last_check: string | null
}

export interface DailyReport {
  id: number
  report_date: string
  status: string
  total_products: number
  top_opportunities: any[]
  market_trends: any
  summary: string | null
  generated_at: string
  sent_at: string | null
}

export { api }