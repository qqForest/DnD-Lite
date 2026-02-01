<template>
  <BasePanel variant="elevated" class="players-lobby-list">
    <template #header>
      <h3 class="panel-title">
        Подключенные игроки
        <span v-if="readyCount > 0" class="ready-count">
          ({{ readyCount }}/{{ sessionStore.otherPlayers.length }} готовы)
        </span>
      </h3>
    </template>
    <div v-if="sessionStore.otherPlayers.length === 0" class="empty-state">
      <Users :size="48" />
      <p>Ожидание подключения игроков...</p>
      <p class="hint">Игроки могут подключиться, используя код сессии</p>
    </div>
    <div v-else class="players-container">
      <div
        v-for="player in sessionStore.otherPlayers"
        :key="player.id"
        class="player-card"
      >
        <div class="player-header" @click="togglePlayer(player.id)">
          <div class="player-info">
            <span :class="['status-dot', { online: player.is_online }]"></span>
            <span class="player-name">{{ player.name }}</span>
            <span :class="['ready-badge', { ready: player.is_ready }]">
              {{ player.is_ready ? '✓ Готов' : '⏳ Не готов' }}
            </span>
          </div>
          <ChevronDown :size="20" :class="{ rotated: expandedPlayers.has(player.id) }" />
        </div>
        <Transition name="expand">
          <div v-if="expandedPlayers.has(player.id)" class="player-characters">
            <div v-if="playerCharacters(player.id).length === 0" class="no-characters">
              У игрока пока нет персонажей
            </div>
            <div v-else class="characters-grid">
              <CharacterCard
                v-for="character in playerCharacters(player.id)"
                :key="character.id"
                :character="character"
              />
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </BasePanel>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Users, ChevronDown } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import BasePanel from '@/components/common/BasePanel.vue'
import CharacterCard from '@/components/character/CharacterCard.vue'

const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()

const expandedPlayers = ref<Set<number>>(new Set())

function togglePlayer(playerId: number) {
  if (expandedPlayers.value.has(playerId)) {
    expandedPlayers.value.delete(playerId)
  } else {
    expandedPlayers.value.add(playerId)
  }
}

const playerCharacters = computed(() => {
  return (playerId: number) => charactersStore.byPlayer(playerId)
})

const readyCount = computed(() => {
  return sessionStore.otherPlayers.filter(p => p.is_ready).length
})
</script>

<style scoped>
.players-lobby-list {
  width: 100%;
}

.panel-title {
  margin: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-8);
  color: var(--color-text-secondary);
  text-align: center;
}

.empty-state svg {
  opacity: 0.5;
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.players-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  max-height: 500px;
  overflow-y: auto;
}

.player-card {
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.player-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-3) var(--spacing-4);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.player-header:hover {
  background: var(--alpha-overlay-light);
}

.player-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  background: var(--color-text-muted);
  flex-shrink: 0;
}

.status-dot.online {
  background: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
}

.player-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.ready-count {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-secondary);
  margin-left: var(--spacing-2);
}

.ready-badge {
  display: inline-flex;
  align-items: center;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  background: var(--color-warning);
  color: var(--color-text-inverse);
  margin-left: var(--spacing-2);
}

.ready-badge.ready {
  background: var(--color-success);
}

.player-characters {
  padding: var(--spacing-4);
  border-top: 1px solid var(--alpha-overlay-light);
  background: var(--color-bg-secondary);
}

.no-characters {
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  padding: var(--spacing-4);
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-3);
}

.rotated {
  transform: rotate(180deg);
}

.expand-enter-active,
.expand-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
  opacity: 1;
}
</style>
