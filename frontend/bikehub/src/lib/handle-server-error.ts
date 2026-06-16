import { AxiosError } from 'axios'
import { toast } from 'sonner'

export function handleServerError(error: unknown) {
  let errMsg = 'Something went wrong!'

  if (error instanceof Error && error.message) {
    errMsg = error.message
  }

  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as { data?: { error?: string; message?: string; title?: string } }).data
    errMsg = data?.error || data?.message || data?.title || errMsg
  }

  if (
    error &&
    typeof error === 'object' &&
    'status' in error &&
    Number(error.status) === 204
  ) {
    errMsg = 'Content not found.'
  }

  if (error instanceof AxiosError) {
    errMsg = error.response?.data.title
  }

  toast.error(errMsg)
}
