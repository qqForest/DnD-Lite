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

    wsService.on('connected', () => {
      isConnected.value = true
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
