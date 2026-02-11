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
          <BaseButton variant="danger" size="sm" @click="showDeleteModal = true">
            Завершить сессию
          </BaseButton>
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

      <div class="maps-section">
        <div class="section-header">
          <h2 class="section-title">Карты</h2>
          <BaseButton variant="secondary" size="sm" @click="showImportMapModal = true">
            Загрузить из профиля
          </BaseButton>
        </div>
        <div v-if="mapStore.loading" class="maps-loading">Загрузка карт...</div>
        <div v-else-if="mapStore.maps.length === 0" class="maps-empty">
          Нет карт. Загрузите карту из профиля, чтобы она была доступна в игре.
        </div>
        <div v-else class="maps-grid">
          <div
            v-for="map in mapStore.maps"
            :key="map.id"
            class="session-map-card"
            :class="{ active: map.is_active }"
            @click="handleSetActiveMap(map.id)"
          >
            <div class="map-card-header">
              <span class="map-card-name">{{ map.name }}</span>
              <span v-if="map.is_active" class="active-badge">Активна</span>
            </div>
            <div class="map-card-info">
              <span>{{ map.width }} x {{ map.height }}</span>
              <span>Сетка: {{ map.grid_scale }}px</span>
            </div>
          </div>
        </div>
      </div>

      <SessionSettings />

      <!-- Temporary: Dice testing -->
      <div class="dice-testing">
        <DiceSelector />
        <RollHistory />
      </div>
    </div>

    <ImportMapModal
      v-model="showImportMapModal"
      @imported="handleMapImported"
    />

    <ConfirmModal
      v-model="showDeleteModal"
      title="Завершить сессию?"
      message="Это отключит всех игроков и удалит сессию навсегда."
      confirm-text="Завершить"
      :danger="true"
      @confirm="handleDeleteSession"
    />

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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useMapStore } from '@/stores/map'
import { useDiceStore } from '@/stores/dice'
import { useWebSocket } from '@/composables/useWebSocket'
import SessionCodeDisplay from '@/components/gm/SessionCodeDisplay.vue'
import PlayersLobbyList from '@/components/gm/PlayersLobbyList.vue'
import NPCSection from '@/components/gm/NPCSection.vue'
import SessionSettings from '@/components/gm/SessionSettings.vue'
import StartGameButton from '@/components/gm/StartGameButton.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import ImportMapModal from '@/components/gm/ImportMapModal.vue'
import DiceSelector from '@/components/dice/DiceSelector.vue'
import RollHistory from '@/components/dice/RollHistory.vue'
import RollResult from '@/components/dice/RollResult.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const mapStore = useMapStore()
const diceStore = useDiceStore()

const showImportMapModal = ref(false)
const showDeleteModal = ref(false)

useWebSocket()

function handleMapImported() {
  mapStore.fetchSessionMaps()
}

async function handleSetActiveMap(mapId: string) {
  try {
    await mapStore.setActiveMap(mapId)
  } catch (error) {
    console.error('Failed to set active map:', error)
  }
}

async function handleDeleteSession() {
  try {
    const { sessionApi } = await import('@/services/api')
    await sessionApi.deleteSession()

    // Close modal
    showDeleteModal.value = false

    // Clear session and redirect immediately
    sessionStore.clearSession()
    router.push({ name: 'dashboard' })
  } catch (error) {
    console.error('Failed to delete session:', error)
    showDeleteModal.value = false
  }
}

onMounted(async () => {
  // Проверка аутентификации
  if (!sessionStore.isAuthenticated || !sessionStore.isGm) {
    router.push({ name: 'dashboard' })
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
    await mapStore.fetchSessionMaps()
  } catch (error) {
    console.error('Failed to load lobby data:', error)
  }

  // Настройка WebSocket handlers
  charactersStore.setupWebSocketHandlers()
  mapStore.setupWebSocketHandlers()
  diceStore.setupWebSocketHandlers()
})

// Setup dice WebSocket on mount
diceStore.setupWebSocketHandlers()
</script>

<style scoped>
.gm-lobby-view {
  min-height: 100vh;
  background: var(--color-bg-primary);
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

.maps-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text-primary);
}

.maps-loading,
.maps-empty {
  text-align: center;
  padding: var(--spacing-6);
  color: var(--color-text-secondary);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
}

.maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--spacing-3);
}

.session-map-card {
  background: var(--color-bg-secondary);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  cursor: pointer;
  transition: border-color 0.2s;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.session-map-card:hover {
  border-color: var(--color-primary);
}

.session-map-card.active {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.map-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.map-card-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.active-badge {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  background: var(--color-primary);
  color: var(--color-text-on-primary, #fff);
  border-radius: var(--radius-full, 999px);
  font-weight: 600;
}

.map-card-info {
  display: flex;
  gap: var(--spacing-3);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
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
