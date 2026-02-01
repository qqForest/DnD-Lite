import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'

export function useAuth() {
  const sessionStore = useSessionStore()

  const getToken = (): string | null => {
    return sessionStore.token || localStorage.getItem('token')
  }

  const setToken = (token: string) => {
    sessionStore.token = token
    localStorage.setItem('token', token)
  }

  const clearToken = () => {
    sessionStore.clearSession()
  }

  const isAuthenticated = computed(() => sessionStore.isAuthenticated)
  const isGm = computed(() => sessionStore.isGm)

  return {
    getToken,
    setToken,
    clearToken,
    isAuthenticated,
    isGm
  }
}
