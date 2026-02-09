<template>
  <PlayerLayout>
    <template #topbar>
      <PlayerTopBar @toggleSidebar="showSidebar = !showSidebar" @leave="showLeaveModal = true" />
    </template>

    <div class="map-container">
      <GameMap :is-read-only="true" />
    </div>

    <template #bottom>
      <div class="bottom-content">
        <!-- Character bar: inventory / flip card / movement -->
        <div class="character-bar">
          <button class="side-btn" title="Инвентарь" disabled>
            <Backpack :size="22" />
          </button>

          <div v-if="characterForCard" class="mini-card-wrapper">
            <CharacterFlipCard :character="characterForCard" :compact="true" />
          </div>
          <div v-else class="mini-card-placeholder">
            <User :size="28" :stroke-width="1.5" />
          </div>

          <div
            class="side-btn movement-indicator"
            :class="{ active: canMove }"
            :title="canMove ? 'Движение разрешено' : 'Движение запрещено'"
          >
            <Footprints :size="22" />
          </div>
        </div>

        <!-- Roll button -->
        <BaseButton variant="primary" size="lg" class="roll-btn" @click="showDiceModal = true">
          <Dice6 :size="20" />
          Бросок
        </BaseButton>

        <!-- Last result -->
        <p v-if="lastResult" class="last-result" @click="showRollDetails">
          Последний: <span class="result-value">{{ lastResult.total }}</span>
          <span class="result-formula">({{ lastResult.formula }})</span>
        </p>
      </div>
    </template>

    <!-- Sidebar -->
    <PlayerSidebar v-model="showSidebar" />

    <!-- Dice Roll Modal -->
    <DiceRollModal v-model="showDiceModal" />

    <!-- Roll Result Modal -->
    <RollResult
      v-if="diceStore.lastResult && showResultModal"
      :result="diceStore.lastResult"
      @close="closeResult"
    />

    <!-- Initiative Roll Modal -->
    <InitiativeRollModal />

    <ConfirmModal
      v-model="showLeaveModal"
      title="Покинуть сессию?"
      message="Вы уверены, что хотите покинуть текущую сессию?"
      confirm-text="Покинуть"
      :danger="true"
      @confirm="handleLeave"
    />
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
import { Dice6, Backpack, Footprints, User } from 'lucide-vue-next'
import type { UserCharacter } from '@/types/models'
import PlayerLayout from '@/layouts/PlayerLayout.vue'
import PlayerTopBar from '@/components/player/PlayerTopBar.vue'
import CharacterFlipCard from '@/components/profile/CharacterFlipCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import DiceRollModal from '@/components/dice/DiceRollModal.vue'
import PlayerSidebar from '@/components/player/PlayerSidebar.vue'
import RollResult from '@/components/dice/RollResult.vue'
import InitiativeRollModal from '@/components/combat/InitiativeRollModal.vue'
import GameMap from '@/components/map/GameMap.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const diceStore = useDiceStore()
const combatStore = useCombatStore()

const showSidebar = ref(false)
const showLeaveModal = ref(false)
const showDiceModal = ref(false)
const showResultModal = computed(() => diceStore.showResult)

// Current player's character
const myCharacter = computed(() => {
  if (!sessionStore.currentPlayer) return null
  const chars = charactersStore.byPlayer(sessionStore.currentPlayer.id)
  return chars.length > 0 ? chars[0] : null
})

// Map Character → UserCharacter for FlipCard
const characterForCard = computed<UserCharacter | null>(() => {
  const ch = myCharacter.value
  if (!ch) return null
  return { ...ch, is_npc: false, user_id: 0, sessions_played: 0, created_at: '' }
})

const canMove = computed(() => sessionStore.currentPlayer?.can_move ?? false)

const lastResult = computed(() => diceStore.lastResult)

function showRollDetails() {
  if (lastResult.value) diceStore.showResult = true
}

function closeResult() {
  diceStore.hideResult()
}

function handleLeave() {
  sessionStore.clearSession()
  router.push({ name: 'profile' })
}

useWebSocket()

onMounted(async () => {
  if (!sessionStore.isAuthenticated) {
    router.push({ name: 'dashboard' })
    return
  }

  if (sessionStore.isGm) {
    router.push({ name: 'gm-lobby' })
    return
  }

  try {
    await sessionStore.fetchSessionState()
    await sessionStore.fetchPlayers()
    await charactersStore.fetchAll()

    if (sessionStore.isAuthenticated) {
      await combatStore.fetchCombatState()
    }
  } catch (error) {
    console.error('Failed to load player data:', error)
  }

  setupWebSocketHandlers()
})

function setupWebSocketHandlers() {
  charactersStore.setupWebSocketHandlers()
  diceStore.setupWebSocketHandlers()
  combatStore.setupWebSocketHandlers()

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

.bottom-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
}

.character-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-4);
  width: 100%;
}

.side-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: var(--alpha-overlay-medium, rgba(255, 255, 255, 0.1));
  color: var(--color-text-muted);
  border: none;
  cursor: default;
  flex-shrink: 0;
}

.side-btn[disabled] {
  opacity: 0.5;
}

.movement-indicator.active {
  color: var(--color-success, #4ade80);
  background: rgba(74, 222, 128, 0.15);
}

.mini-card-wrapper {
  width: 120px;
  flex-shrink: 0;
}

.mini-card-placeholder {
  width: 120px;
  aspect-ratio: 3 / 4;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  background: var(--color-bg-secondary);
  border: 1px dashed var(--color-border);
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.roll-btn {
  width: 100%;
  max-width: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  font-weight: var(--font-weight-semibold, 600);
}

.last-result {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  margin: 0;
  -webkit-tap-highlight-color: transparent;
}

.last-result:active {
  opacity: 0.7;
}

.result-value {
  font-family: var(--font-family-mono, monospace);
  font-weight: 700;
  color: var(--color-accent-primary, #e94560);
}

.result-formula {
  color: var(--color-text-muted);
}
</style>
