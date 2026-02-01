import type { AxiosError } from 'axios'

export interface ApiError {
  detail: string
}

export interface ApiResponse<T> {
  data: T
  status: number
  statusText: string
}

export type ApiErrorResponse = AxiosError<ApiError>
