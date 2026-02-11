import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Session, Player, SessionResponse, SessionJoinResponse } from '@/types/models'
import { sessionApi } from '@/services/api'
import { wsService } from '@/services/websocket'
import router from '@/router'

export const useSessionStore = defineStore('session', () => {
  const id = ref<number | null>(null)
  const playerId = ref<number | null>(localStorage.getItem('playerId') ? parseInt(localStorage.getItem('playerId')!) : null)
  const code = ref<string | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const accessToken = ref<string | null>(localStorage.getItem('accessToken'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const isGm = ref<boolean>(localStorage.getItem('isGm') === 'true')
  const players = ref<Player[]>([])
  const isConnected = ref<boolean>(false)
  const sessionState = ref<Session | null>(null)
  const sessionStarted = ref<boolean>(false)
  const characterId = ref<number | null>(null)

  // Восстанавливаем session tokens если пользователь в сессии
  if (token.value) {
    const sessionAccessToken = localStorage.getItem('sessionAccessToken')
    const sessionRefreshToken = localStorage.getItem('sessionRefreshToken')
    if (sessionAccessToken && sessionRefreshToken) {
      localStorage.setItem('accessToken', sessionAccessToken)
      localStorage.setItem('refreshToken', sessionRefreshToken)
      accessToken.value = sessionAccessToken
      refreshToken.value = sessionRefreshToken
    }
  }

  const isAuthenticated = computed(() => !!token.value)

  const currentPlayer = computed(() => {
    return players.value.find(p => p.id === playerId.value)
  })

  const otherPlayers = computed(() => {
    return players.value.filter(p => !p.is_gm)
  })

  const isReady = computed(() => {
    return currentPlayer.value?.is_ready ?? false
  })

  async function createSession(userMapId?: string) {
    const data = userMapId ? { user_map_id: userMapId } : undefined
    const response: SessionResponse = await sessionApi.createSession(data)
    code.value = response.code
    token.value = response.gm_token
    isGm.value = true
    localStorage.setItem('isGm', 'true')
    localStorage.setItem('code', response.code)

    // Сохраняем пользовательские токены перед перезаписью сессионными
    saveUserTokens()

    // Сохраняем session tokens отдельно для восстановления
    localStorage.setItem('token', response.gm_token)
    localStorage.setItem('sessionAccessToken', response.access_token)
    localStorage.setItem('sessionRefreshToken', response.refresh_token)

    // Устанавливаем session tokens как активные
    localStorage.setItem('accessToken', response.access_token)
    localStorage.setItem('refreshToken', response.refresh_token)
    accessToken.value = response.access_token
    refreshToken.value = response.refresh_token

    await connectWebSocket()
    await fetchSessionState()
    await fetchPlayers()

    const gmPlayer = players.value.find(p => p.is_gm)
    if (gmPlayer) {
      playerId.value = gmPlayer.id
      localStorage.setItem('playerId', gmPlayer.id.toString())
    }
  }

  async function joinSession(sessionCode: string, name: string, userCharacterId?: number) {
    const response: SessionJoinResponse = await sessionApi.joinSession({
      code: sessionCode,
      name,
      user_character_id: userCharacterId
    })
    token.value = response.token
    code.value = response.session_code
    playerId.value = response.player_id
    isGm.value = false
    localStorage.setItem('isGm', 'false')
    localStorage.setItem('code', response.session_code)
    if (response.character_id) {
      characterId.value = response.character_id
    }
    // Сохраняем пользовательские токены перед перезаписью сессионными
    saveUserTokens()

    // Сохраняем session tokens отдельно для восстановления
    localStorage.setItem('token', response.token)
    localStorage.setItem('sessionAccessToken', response.access_token)
    localStorage.setItem('sessionRefreshToken', response.refresh_token)
    localStorage.setItem('playerId', response.player_id.toString())

    // Устанавливаем session tokens как активные
    localStorage.setItem('accessToken', response.access_token)
    localStorage.setItem('refreshToken', response.refresh_token)
    accessToken.value = response.access_token
    refreshToken.value = response.refresh_token

    await connectWebSocket()
    await fetchSessionState()
    await fetchPlayers()
  }

  async function fetchSessionState() {
    if (!token.value) return
    try {
      sessionState.value = await sessionApi.getSessionState()
      id.value = sessionState.value.id
      code.value = sessionState.value.code
      sessionStarted.value = sessionState.value.session_started
      if (sessionState.value.player_id) {
        playerId.value = sessionState.value.player_id
        localStorage.setItem('playerId', playerId.value.toString())
      }
      if (sessionState.value.is_gm !== undefined) {
        isGm.value = sessionState.value.is_gm
        localStorage.setItem('isGm', sessionState.value.is_gm.toString())
      }
    } catch (error) {
      console.error('Failed to fetch session state:', error)
    }
  }

  async function startSession() {
    if (!token.value) throw new Error('Not authenticated')
    if (!isGm.value) throw new Error('Only GM can start session')

    try {
      await sessionApi.startSession()
      sessionStarted.value = true
      if (sessionState.value) {
        sessionState.value.session_started = true
      }
    } catch (error) {
      console.error('Failed to start session:', error)
      throw error
    }
  }

  async function fetchPlayers() {
    if (!token.value) return
    try {
      players.value = await sessionApi.getPlayers()
    } catch (error) {
      console.error('Failed to fetch players:', error)
    }
  }

  async function setReady(isReady: boolean) {
    if (!token.value) throw new Error('Not authenticated')
    if (isGm.value) throw new Error('GM cannot set ready status')

    try {
      await sessionApi.setReady(isReady)
      // Обновляем локальное состояние
      if (currentPlayer.value) {
        currentPlayer.value.is_ready = isReady
      }
      // Обновляем в массиве players
      const index = players.value.findIndex(p => p.id === currentPlayer.value?.id)
      if (index > -1) {
        players.value[index].is_ready = isReady
      }
    } catch (error) {
      console.error('Failed to set ready status:', error)
      throw error
    }
  }

  const isHandlersSetup = ref<boolean>(false)

  function setupWebSocketHandlers() {
    if (isHandlersSetup.value) return
    isHandlersSetup.value = true

    wsService.on('connected', () => {
      isConnected.value = true
    })

    wsService.on('disconnected', () => {
      isConnected.value = false
    })

    wsService.on('player_joined', (data: { player_id: number; player_name: string; is_gm: boolean }) => {
      const existingIndex = players.value.findIndex(p => p.id === data.player_id)
      if (existingIndex === -1) {
        players.value.push({
          id: data.player_id,
          name: data.player_name,
          is_gm: data.is_gm,
          is_online: true,
          is_ready: false
        })
      } else {
        players.value[existingIndex].is_online = true
      }
    })

    wsService.on('player_left', (data: { player_id: number }) => {
      const index = players.value.findIndex(p => p.id === data.player_id)
      if (index > -1) {
        players.value[index].is_online = false
      }
    })

    wsService.on('player_ready', (data: { player_id: number; player_name: string; is_ready: boolean }) => {
      const index = players.value.findIndex(p => p.id === data.player_id)
      if (index > -1) {
        players.value[index].is_ready = data.is_ready
      }
    })

    wsService.on('player_movement_changed', (data: { player_id: number; can_move: boolean }) => {
      const player = players.value.find(p => p.id === data.player_id)
      if (player) {
        player.can_move = data.can_move
      }
    })

    wsService.on('session_deleted', (data: { session_id: number; message: string }) => {
      // Clear session
      clearSession()

      // Redirect to dashboard
      router.push({ name: 'dashboard' })
    })

    wsService.on('leave_confirmed', () => {
      console.log('Leave confirmed by server')
    })
  }

  function connectWebSocket() {
    if (!token.value) return

    // Don't reconnect if already connected/connecting with the same token
    if (!wsService.isActiveFor(token.value)) {
      wsService.disconnect()
      wsService.connect(token.value)
    }

    setupWebSocketHandlers()
  }

  function saveUserTokens() {
    const currentAccess = localStorage.getItem('accessToken')
    const currentRefresh = localStorage.getItem('refreshToken')
    if (currentAccess) {
      localStorage.setItem('userAccessToken', currentAccess)
    }
    if (currentRefresh) {
      localStorage.setItem('userRefreshToken', currentRefresh)
    }
  }

  async function tryRestoreSession(codeFromUrl?: string): Promise<boolean> {
    const storedToken = localStorage.getItem('token')
    const storedCode = localStorage.getItem('code')

    if (!storedToken) return false
    if (codeFromUrl && storedCode !== codeFromUrl.toUpperCase()) return false

    token.value = storedToken
    code.value = storedCode

    try {
      await fetchSessionState()
      await connectWebSocket()
      await fetchPlayers()
      return true
    } catch (error: any) {
      if (error.response?.status === 404) {
        console.log('Session no longer exists')
      }
      clearSession()
      return false
    }
  }

  function clearSession() {
    // Send explicit leave before disconnect
    if (token.value && wsService.isConnected) {
      wsService.send('explicit_leave', {})
      // Small delay to allow message to send
      setTimeout(() => wsService.disconnect(), 100)
    } else {
      wsService.disconnect()
    }

    id.value = null
    playerId.value = null
    code.value = null
    token.value = null
    isGm.value = false
    players.value = []
    isConnected.value = false
    sessionState.value = null
    sessionStarted.value = false
    characterId.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('playerId')
    localStorage.removeItem('isGm')
    localStorage.removeItem('code')
    localStorage.removeItem('sessionAccessToken')
    localStorage.removeItem('sessionRefreshToken')

    // Восстанавливаем пользовательские токены вместо удаления
    const savedAccess = localStorage.getItem('userAccessToken')
    const savedRefresh = localStorage.getItem('userRefreshToken')
    if (savedAccess) {
      localStorage.setItem('accessToken', savedAccess)
      accessToken.value = savedAccess
    } else {
      localStorage.removeItem('accessToken')
      accessToken.value = null
    }
    if (savedRefresh) {
      localStorage.setItem('refreshToken', savedRefresh)
      refreshToken.value = savedRefresh
    } else {
      localStorage.removeItem('refreshToken')
      refreshToken.value = null
    }
  }

  return {
    id,
    playerId,
    code,
    token,
    isGm,
    players,
    isConnected,
    sessionState,
    sessionStarted,
    characterId,
    isAuthenticated,
    currentPlayer,
    otherPlayers,
    isReady,
    createSession,
    joinSession,
    fetchSessionState,
    fetchPlayers,
    startSession,
    setReady,
    connectWebSocket,
    setupWebSocketHandlers,
    tryRestoreSession,
    clearSession
  }
})
