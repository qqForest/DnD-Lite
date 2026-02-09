<template>
  <GMLayout @leave="showLeaveModal = true">
    <template #initiative-bar>
      <InitiativeBar />
    </template>

    <div class="gm-content">
      <GameMap />
    </div>

    <!-- Roll Result Modal -->
    <RollResult
      v-if="diceStore.lastResult && showResultModal"
      :result="diceStore.lastResult"
      @close="closeResult"
    />

    <ConfirmModal
      v-model="showLeaveModal"
      title="Покинуть сессию?"
      message="Вы уверены, что хотите покинуть текущую сессию?"
      confirm-text="Покинуть"
      :danger="true"
      @confirm="handleLeave"
    />
  </GMLayout>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useDiceStore } from '@/stores/dice'
import { useCombatStore } from '@/stores/combat'
import { useWebSocket } from '@/composables/useWebSocket'
import GMLayout from '@/layouts/GMLayout.vue'
import RollResult from '@/components/dice/RollResult.vue'
import InitiativeBar from '@/components/combat/InitiativeBar.vue'
import GameMap from '@/components/map/GameMap.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const diceStore = useDiceStore()
const combatStore = useCombatStore()

const showLeaveModal = ref(false)
const showResultModal = computed(() => diceStore.showResult)

function closeResult() {
  diceStore.hideResult()
}

function handleLeave() {
  sessionStore.clearSession()
  router.push({ name: 'profile' })
}

useWebSocket()

onMounted(async () => {
  // Проверка аутентификации
  if (!sessionStore.isAuthenticated || !sessionStore.isGm) {
    router.push({ name: 'dashboard' })
    return
  }

  // Загрузка данных
  try {
    await sessionStore.fetchSessionState()
    
    // Если сессия не начата, редирект на лобби
    if (!sessionStore.sessionStarted) {
      router.push({ name: 'gm-lobby' })
      return
    }
    
    await sessionStore.fetchPlayers()
    await charactersStore.fetchAll()
    
    // Check combat state and fetch initiative list
    if (sessionStore.isAuthenticated) {
      await combatStore.fetchCombatState()
      if (combatStore.isActive) {
        await combatStore.fetchInitiativeList()
      }
    }
  } catch (error) {
    console.error('Failed to load GM data:', error)
  }

  // Настройка WebSocket handlers
  charactersStore.setupWebSocketHandlers()
  diceStore.setupWebSocketHandlers()
  combatStore.setupWebSocketHandlers()
})
</script>

<style scoped>
.gm-content {
  position: relative;
  height: 100%;
  width: 100%;
}

.map-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-top: var(--spacing-2);
}
</style>
