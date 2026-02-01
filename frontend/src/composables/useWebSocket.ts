import { ref, onMounted, onUnmounted } from 'vue'
import { wsService } from '@/services/websocket'
import { useSessionStore } from '@/stores/session'

export function useWebSocket() {
  const sessionStore = useSessionStore()
  const isConnected = ref(false)

  const connect = () => {
    if (sessionStore.token) {
      wsService.connect(sessionStore.token)
    }
  }

  const disconnect = () => {
    wsService.disconnect()
  }

  const send = (event: string, data: any) => {
    wsService.send(event, data)
  }

  const on = (event: string, handler: (data: any) => void) => {
    wsService.on(event, handler)
  }

  const off = (event: string, handler: (data: any) => void) => {
    wsService.off(event, handler)
  }

  onMounted(() => {
    if (sessionStore.token) {
      connect()
    }

    wsService.on('connected', async () => {
      isConnected.value = true
      // Setup handlers for all stores when connected
      const charactersStore = (await import('@/stores/characters')).useCharactersStore()
      const diceStore = (await import('@/stores/dice')).useDiceStore()

      charactersStore.setupWebSocketHandlers()
      diceStore.setupWebSocketHandlers()
    })

    wsService.on('disconnected', () => {
      isConnected.value = false
    })
  })

  onUnmounted(() => {
    // Don't disconnect on unmount - keep connection alive
    // disconnect()
  })

  return {
    isConnected,
    connect,
    disconnect,
    send,
    on,
    off
  }
}
