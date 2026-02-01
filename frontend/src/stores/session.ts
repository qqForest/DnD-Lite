import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Session, Player, SessionResponse, SessionJoinResponse } from '@/types/models'
import { sessionApi } from '@/services/api'
import { wsService } from '@/services/websocket'

export const useSessionStore = defineStore('session', () => {
  const id = ref<number | null>(null)
  const code = ref<string | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isGm = ref<boolean>(false)
  const players = ref<Player[]>([])
  const isConnected = ref<boolean>(false)
  const sessionState = ref<Session | null>(null)
  const sessionStarted = ref<boolean>(false)

  const isAuthenticated = computed(() => !!token.value)

  const currentPlayer = computed(() => {
    return players.value.find(p => p.is_gm === isGm.value)
  })

  const otherPlayers = computed(() => {
    return players.value.filter(p => !p.is_gm)
  })

  const isReady = computed(() => {
    return currentPlayer.value?.is_ready ?? false
  })

  async function createSession() {
    const response: SessionResponse = await sessionApi.createSession()
    code.value = response.code
    token.value = response.gm_token
    isGm.value = true
    localStorage.setItem('token', response.gm_token)
    await connectWebSocket()
    await fetchSessionState()
    await fetchPlayers()
  }

  async function joinSession(sessionCode: string, name: string) {
    const response: SessionJoinResponse = await sessionApi.joinSession({
      code: sessionCode,
      name
    })
    token.value = response.token
    code.value = response.session_code
    isGm.value = false
    localStorage.setItem('token', response.token)
    await connectWebSocket()
    await fetchSessionState()
    await fetchPlayers()
  }

  async function fetchSessionState() {
    if (!token.value) return
    try {
      sessionState.value = await sessionApi.getSessionState(token.value)
      id.value = sessionState.value.id
      code.value = sessionState.value.code
      sessionStarted.value = sessionState.value.session_started
    } catch (error) {
      console.error('Failed to fetch session state:', error)
    }
  }

  async function startSession() {
    if (!token.value) throw new Error('Not authenticated')
    if (!isGm.value) throw new Error('Only GM can start session')
    
    try {
      await sessionApi.startSession(token.value)
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
      players.value = await sessionApi.getPlayers(token.value)
    } catch (error) {
      console.error('Failed to fetch players:', error)
    }
  }

  async function setReady(isReady: boolean) {
    if (!token.value) throw new Error('Not authenticated')
    if (isGm.value) throw new Error('GM cannot set ready status')
    
    try {
      await sessionApi.setReady(isReady, token.value)
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

  function connectWebSocket() {
    if (!token.value) return
    
    wsService.disconnect()
    wsService.connect(token.value)

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
  }

  function clearSession() {
    id.value = null
    code.value = null
    token.value = null
    isGm.value = false
    players.value = []
    isConnected.value = false
    sessionState.value = null
    localStorage.removeItem('token')
    wsService.disconnect()
  }

  return {
    id,
    code,
    token,
    isGm,
    players,
    isConnected,
    sessionState,
    sessionStarted,
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
    clearSession
  }
})
