import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/models'
import { authApi } from '@/services/api'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => !!user.value)

  async function register(username: string, displayName: string, password: string, role: string) {
    const response = await authApi.register({
      username,
      display_name: displayName,
      password,
      role,
    })
    user.value = response.user
    localStorage.setItem('accessToken', response.access_token)
    localStorage.setItem('refreshToken', response.refresh_token)
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  async function login(username: string, password: string) {
    const response = await authApi.login({ username, password })
    user.value = response.user
    localStorage.setItem('accessToken', response.access_token)
    localStorage.setItem('refreshToken', response.refresh_token)
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  async function fetchMe() {
    try {
      const userData = await authApi.getMe()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userAccessToken')
    localStorage.removeItem('userRefreshToken')
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('playerId')
  }

  function restoreFromStorage() {
    const stored = localStorage.getItem('user')
    if (stored) {
      try {
        user.value = JSON.parse(stored)
      } catch {
        user.value = null
      }
    }
  }

  // Восстанавливаем при создании store
  restoreFromStorage()

  return {
    user,
    isLoggedIn,
    register,
    login,
    logout,
    fetchMe,
    restoreFromStorage,
  }
})
