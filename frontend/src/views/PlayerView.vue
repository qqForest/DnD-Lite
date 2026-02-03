<template>
  <PlayerLayout>
    <template #topbar>
      <PlayerTopBar @toggleSidebar="showSidebar = !showSidebar" />
    </template>

    <div class="map-container">
      <GameMap :is-read-only="true" />
    </div>

    <template #bottom>
      <div class="bottom-content">
        <CharacterSheet />
        <PlayerDiceSelector />
      </div>
    </template>

    <!-- Sidebar -->
    <PlayerSidebar v-model="showSidebar" />

    <!-- Roll Result Modal -->
    <RollResult
      v-if="diceStore.lastResult && showResultModal"
      :result="diceStore.lastResult"
      @close="closeResult"
    />

    <!-- Initiative Roll Modal -->
    <InitiativeRollModal />
  </PlayerLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useDiceStore } from '@/stores/dice'
import { useCombatStore } from '@/stores/combat'
import { useWebSocket } from '@/composables/useWebSocket'
import { wsService } from '@/services/websocket'
import PlayerLayout from '@/layouts/PlayerLayout.vue'
import PlayerTopBar from '@/components/player/PlayerTopBar.vue'
import CharacterSheet from '@/components/player/CharacterSheet.vue'
import PlayerDiceSelector from '@/components/player/PlayerDiceSelector.vue'
import PlayerSidebar from '@/components/player/PlayerSidebar.vue'
import RollResult from '@/components/dice/RollResult.vue'
import InitiativeRollModal from '@/components/combat/InitiativeRollModal.vue'
import GameMap from '@/components/map/GameMap.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const diceStore = useDiceStore()
const combatStore = useCombatStore()

const showSidebar = ref(false)
const showResultModal = computed(() => diceStore.showResult)

function closeResult() {
  diceStore.hideResult()
}

useWebSocket()

onMounted(async () => {
  // Проверка аутентификации
  if (!sessionStore.isAuthenticated) {
    router.push({ name: 'home' })
    return
  }

  // Если GM пытается зайти на страницу игрока - редирект
  if (sessionStore.isGm) {
    router.push({ name: 'gm-lobby' })
    return
  }

  // Загрузка данных
  try {
    await sessionStore.fetchSessionState()
    await sessionStore.fetchPlayers()
    await charactersStore.fetchAll()
    
    // Check if combat is active
    if (sessionStore.isAuthenticated) {
      await combatStore.fetchCombatState()
    }
  } catch (error) {
    console.error('Failed to load player data:', error)
  }

  // Настройка WebSocket handlers
  setupWebSocketHandlers()
})

function setupWebSocketHandlers() {
  // Handlers для персонажей
  charactersStore.setupWebSocketHandlers()

  // Handlers для кубиков
  diceStore.setupWebSocketHandlers()

  // Handlers для боя
  combatStore.setupWebSocketHandlers()

  // Дополнительные handlers для игрока
  wsService.on('session_started', () => {
    sessionStore.sessionStarted = true
    if (sessionStore.sessionState) {
      sessionStore.sessionState.session_started = true
    }
  })
}

onUnmounted(() => {
  // Cleanup при необходимости
})
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-top: var(--spacing-2);
}

.bottom-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3) var(--spacing-4);
  height: 100%;
}

.bottom-content > :first-child {
  flex: 1;
}

@media (max-width: 768px) {
  .bottom-content {
    flex-direction: column;
    gap: var(--spacing-2);
    padding: var(--spacing-2);
  }
}
</style>
