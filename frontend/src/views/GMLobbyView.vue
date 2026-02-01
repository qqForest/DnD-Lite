<template>
  <div class="gm-lobby-view">
    <div class="fixed-header">
      <div class="fixed-header-content">
        <h1 class="lobby-title">Лобби сессии</h1>
        <div class="header-actions">
          <div class="header-info">
            <span v-if="sessionStore.isConnected" class="connection-status connected">
              ● Подключено
            </span>
            <span v-else class="connection-status disconnected">
              ○ Отключено
            </span>
          </div>
          <StartGameButton />
        </div>
      </div>
    </div>

    <div class="lobby-container">
      <div class="lobby-spacer"></div>

      <SessionCodeDisplay />

      <div class="lobby-content">
        <div class="left-column">
          <PlayersLobbyList />
        </div>
        <div class="right-column">
          <NPCSection />
        </div>
      </div>

      <SessionSettings />

      <!-- Temporary: Dice testing -->
      <div class="dice-testing">
        <DiceSelector />
        <RollHistory />
      </div>
    </div>

    <!-- Roll Result Modal -->
    <RollResult
      v-if="diceStore.lastResult"
      :result="diceStore.lastResult"
      :visible="diceStore.showResult"
      @close="diceStore.hideResult()"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useDiceStore } from '@/stores/dice'
import { useWebSocket } from '@/composables/useWebSocket'
import SessionCodeDisplay from '@/components/gm/SessionCodeDisplay.vue'
import PlayersLobbyList from '@/components/gm/PlayersLobbyList.vue'
import NPCSection from '@/components/gm/NPCSection.vue'
import SessionSettings from '@/components/gm/SessionSettings.vue'
import StartGameButton from '@/components/gm/StartGameButton.vue'
import DiceSelector from '@/components/dice/DiceSelector.vue'
import RollHistory from '@/components/dice/RollHistory.vue'
import RollResult from '@/components/dice/RollResult.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const diceStore = useDiceStore()

useWebSocket()

onMounted(async () => {
  // Проверка аутентификации
  if (!sessionStore.isAuthenticated || !sessionStore.isGm) {
    router.push({ name: 'home' })
    return
  }

  // Если сессия уже начата, редирект на основной интерфейс
  await sessionStore.fetchSessionState()
  if (sessionStore.sessionStarted) {
    router.push({ name: 'gm' })
    return
  }

  // Загрузка данных
  try {
    await sessionStore.fetchPlayers()
    await charactersStore.fetchAll()
  } catch (error) {
    console.error('Failed to load lobby data:', error)
  }

  // Настройка WebSocket handlers
  charactersStore.setupWebSocketHandlers()
  diceStore.setupWebSocketHandlers()
})

// Setup dice WebSocket on mount
diceStore.setupWebSocketHandlers()
</script>

<style scoped>
.gm-lobby-view {
  min-height: 100vh;
  height: 100vh;
  background: var(--color-bg-primary);
  overflow-y: auto;
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--alpha-overlay-medium);
  box-shadow: var(--shadow-sm);
}

.fixed-header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-4) var(--spacing-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
}

.lobby-spacer {
  height: 100px;
}

.lobby-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.lobby-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.header-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.connection-status {
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.connection-status.connected {
  color: var(--color-success);
}

.connection-status.disconnected {
  color: var(--color-text-muted);
}

.lobby-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-6);
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
}

@media (max-width: 1024px) {
  .fixed-header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-3);
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .lobby-content {
    grid-template-columns: 1fr;
  }

  .lobby-spacer {
    height: 140px;
  }
}

.dice-testing {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-6);
}

@media (max-width: 1024px) {
  .dice-testing {
    grid-template-columns: 1fr;
  }
}
</style>
