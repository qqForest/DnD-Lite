import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DiceResult, DiceRoll } from '@/types/models'
import { diceApi } from '@/services/api'
import { wsService } from '@/services/websocket'
import { useSessionStore } from './session'

export const useDiceStore = defineStore('dice', () => {
  const history = ref<DiceResult[]>([])
  const lastResult = ref<DiceResult | null>(null)
  const showResult = ref(false)

  async function roll(notation: string, reason?: string) {
    const sessionStore = useSessionStore()
    if (!sessionStore.token) throw new Error('Not authenticated')

    try {
      const result = await diceApi.roll({ dice: notation, reason: reason || null }, sessionStore.token)
      // Don't add to history or show result here - will be handled via WebSocket
      // This ensures all clients (including the roller) see it at the same time
      return result
    } catch (error) {
      console.error('Failed to roll dice:', error)
      throw error
    }
  }

  // Alias для обратной совместимости
  const rollDice = roll

  function setupWebSocketHandlers() {
    wsService.on('dice_result', (data: DiceResult) => {
      lastResult.value = data
      history.value.unshift(data)
      showResult.value = true

      // Keep only last 50 rolls
      if (history.value.length > 50) {
        history.value = history.value.slice(0, 50)
      }
    })
  }

  function clearHistory() {
    history.value = []
    lastResult.value = null
  }

  function hideResult() {
    showResult.value = false
  }

  return {
    history,
    lastResult,
    showResult,
    roll,
    rollDice,
    setupWebSocketHandlers,
    clearHistory,
    hideResult
  }
})
