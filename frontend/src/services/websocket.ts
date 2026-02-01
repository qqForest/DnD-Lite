// WebSocket service for real-time communication

type EventHandler = (data: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnects = 5
  private reconnectTimeout: number | null = null
  private eventHandlers: Map<string, EventHandler[]> = new Map()
  private token: string | null = null

  connect(token: string) {
    this.token = token
    let wsUrl = import.meta.env.VITE_WS_URL

    if (!wsUrl) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      // If we are in dev mode (usually port 3000), default to localhost:8000 for backend
      // Otherwise use the current host
      if (host.includes('localhost:3000') || host.includes('127.0.0.1:3000')) {
        wsUrl = `${protocol}//${window.location.hostname}:8000`
      } else {
        wsUrl = `${protocol}//${host}`
      }
    }

    const url = `${wsUrl}/ws?token=${token}`
    console.log(`Connecting to WebSocket: ${url}`)

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.emit('connected', {})
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.emit('disconnected', {})
      this.attemptReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.emit('error', { error })
    }
  }

  private handleMessage(message: { event?: string; type?: string; payload?: any; data?: any }) {
    const eventType = message.event || message.type
    const data = message.payload || message.data || message

    if (eventType) {
      this.emit(eventType, data)
    }
  }

  send(event: string, data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: event, payload: data }))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  on(event: string, handler: EventHandler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, [])
    }
    const handlers = this.eventHandlers.get(event)!
    if (!handlers.includes(handler)) {
      handlers.push(handler)
    }
  }

  off(event: string, handler: EventHandler) {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  offAll(event?: string) {
    if (event) {
      this.eventHandlers.delete(event)
    } else {
      this.eventHandlers.clear()
    }
  }

  private emit(event: string, data: any) {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => handler(data))
    }
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnects && this.token) {
      this.reconnectAttempts++
      const delay = 2000 * this.reconnectAttempts
      console.log(`Attempting to reconnect in ${delay}ms... (attempt ${this.reconnectAttempts}/${this.maxReconnects})`)

      this.reconnectTimeout = window.setTimeout(() => {
        if (this.token) {
          this.connect(this.token)
        }
      }, delay)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsService = new WebSocketService()
export default wsService
