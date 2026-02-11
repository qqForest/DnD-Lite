<template>
  <div class="player-lobby-view">
    <PlayerLobbyTopBar @toggle-sidebar="showSidebar = !showSidebar" />

    <div class="lobby-content">
      <h2 class="section-title">Ваш персонаж</h2>

      <div v-if="characterForCard" class="card-wrapper">
        <CharacterFlipCard :character="characterForCard" />
      </div>
      <p v-else class="no-character">Персонаж не выбран</p>

      <BaseButton
        :variant="sessionStore.isReady ? 'primary' : 'secondary'"
        size="lg"
        :disabled="!myCharacter || readySetting"
        class="ready-btn"
        @click="toggleReady"
      >
        <CheckCircle v-if="sessionStore.isReady" :size="20" />
        <Circle v-else :size="20" />
        {{ readySetting ? 'Обновление...' : sessionStore.isReady ? 'Готов' : 'Не готов' }}
      </BaseButton>

      <p class="ready-count">{{ readyCountText }}</p>

      <div class="session-code">
        <span class="session-code-label">Код сессии</span>
        <button class="session-code-value" @click="copyCode">
          <span>{{ sessionStore.code || '---' }}</span>
          <Copy :size="16" />
        </button>
      </div>
    </div>

    <PlayerLobbySidebar
      v-model="showSidebar"
      @leave="showLeaveModal = true"
    />

    <ConfirmModal
      v-model="showLeaveModal"
      title="Покинуть сессию?"
      message="Вы уверены, что хотите покинуть текущую сессию?"
      confirm-text="Покинуть"
      :danger="true"
      @confirm="handleLeave"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { CheckCircle, Circle, Copy } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useWebSocket } from '@/composables/useWebSocket'
import { useToast } from '@/composables/useToast'
import { wsService } from '@/services/websocket'
import type { UserCharacter } from '@/types/models'
import PlayerLobbyTopBar from '@/components/player/PlayerLobbyTopBar.vue'
import PlayerLobbySidebar from '@/components/player/PlayerLobbySidebar.vue'
import CharacterFlipCard from '@/components/profile/CharacterFlipCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const toast = useToast()

const showSidebar = ref(false)
const showLeaveModal = ref(false)
const readySetting = ref(false)

const myCharacter = computed(() => {
  if (!sessionStore.currentPlayer) return null
  const chars = charactersStore.byPlayer(sessionStore.currentPlayer.id)
  return chars.length > 0 ? chars[0] : null
})

const characterForCard = computed<UserCharacter | null>(() => {
  const ch = myCharacter.value
  if (!ch) return null
  return {
    ...ch,
    is_npc: false,
    user_id: 0,
    sessions_played: 0,
    created_at: '',
  }
})

const readyCountText = computed(() => {
  const nonGmPlayers = sessionStore.players.filter(p => !p.is_gm)
  const readyCount = nonGmPlayers.filter(p => p.is_ready).length
  const total = nonGmPlayers.length
  return `${readyCount} из ${total} игроков готовы`
})

useWebSocket()

async function toggleReady() {
  if (!myCharacter.value || readySetting.value) return
  readySetting.value = true
  try {
    await sessionStore.setReady(!sessionStore.isReady)
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Не удалось изменить статус готовности')
  } finally {
    readySetting.value = false
  }
}

async function copyCode() {
  if (!sessionStore.code) return
  try {
    await navigator.clipboard.writeText(sessionStore.code)
    toast.success('Код скопирован')
  } catch {
    toast.error('Не удалось скопировать')
  }
}

function handleLeave() {
  sessionStore.clearSession()
  router.push({ name: 'profile' })
}

onMounted(async () => {
  if (!sessionStore.isAuthenticated) {
    router.push({ name: 'dashboard' })
    return
  }

  if (sessionStore.isGm) {
    router.push({
      name: 'gm-lobby-with-code',
      params: { code: sessionStore.code }
    })
    return
  }

  await sessionStore.fetchSessionState()
  if (sessionStore.sessionStarted) {
    router.push({
      name: 'player-with-code',
      params: { code: sessionStore.code }
    })
    return
  }

  try {
    await sessionStore.fetchPlayers()
    await charactersStore.fetchAll()
  } catch (error) {
    console.error('Failed to load lobby data:', error)
  }

  // Fix бага: авто-выбор персонажа для корректной работы кнопки "Готов"
  if (sessionStore.currentPlayer) {
    const chars = charactersStore.byPlayer(sessionStore.currentPlayer.id)
    if (chars.length > 0) {
      charactersStore.select(chars[0].id)
    }
  }

  setupWebSocketHandlers()
})

function setupWebSocketHandlers() {
  charactersStore.setupWebSocketHandlers()

  wsService.on('session_started', () => {
    sessionStore.sessionStarted = true
    if (sessionStore.sessionState) {
      sessionStore.sessionState.session_started = true
    }
    router.push({
      name: 'player-with-code',
      params: { code: sessionStore.code }
    })
  })
}
</script>

<style scoped>
.player-lobby-view {
  min-height: 100vh;
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
}

.lobby-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-6) var(--spacing-4);
  gap: var(--spacing-4);
}

.section-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  align-self: flex-start;
}

.card-wrapper {
  width: 100%;
  max-width: 300px;
}

.no-character {
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
  padding: var(--spacing-8) 0;
  margin: 0;
}

.ready-btn {
  width: 100%;
  max-width: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  font-weight: var(--font-weight-semibold);
}

.ready-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.session-code {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-4);
}

.session-code-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.session-code-value {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  font-family: monospace;
  font-size: var(--font-size-xl);
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--color-accent-primary);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast);
  -webkit-tap-highlight-color: transparent;
}

.session-code-value:active {
  transform: scale(0.97);
}
</style>
