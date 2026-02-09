<template>
  <div class="players-tab">
    <h3 class="section-title">Игроки</h3>
    <div v-if="sessionStore.players.length === 0" class="empty-state">
      Нет подключенных игроков
    </div>
    <div v-else class="players-list">
      <div
        v-for="player in sessionStore.players"
        :key="player.id"
        :class="['player-item', { 'is-gm': player.is_gm, 'is-online': player.is_online }]"
      >
        <div class="player-status">
          <span :class="['status-dot', { online: player.is_online }]"></span>
        </div>
        <div class="player-avatar-slot">
          <img
            v-if="playerAvatar(player.id)"
            :src="playerAvatar(player.id)!"
            class="player-avatar-img"
          />
          <span v-else class="player-avatar-placeholder">
            {{ player.name.charAt(0).toUpperCase() }}
          </span>
        </div>
        <div class="player-info">
          <div class="player-name">
            {{ player.name }}
            <span v-if="player.is_gm" class="gm-badge">GM</span>
            <span v-if="!player.is_gm && player.can_move" class="move-badge">
              <Move :size="10" />
            </span>
          </div>
          <div v-if="charactersStore.byPlayer(player.id).length > 0" class="player-characters">
            {{ charactersStore.byPlayer(player.id)[0].name }}
            <span v-if="(charactersStore.byPlayer(player.id)[0] as any).armor_class" class="ac-mini">
              <svg viewBox="0 0 40 46" class="ac-mini-svg">
                <path
                  d="M20 2 L38 10 L38 24 C38 34 28 42 20 44 C12 42 2 34 2 24 L2 10 Z"
                  fill="var(--color-bg-primary, #12121a)"
                  stroke="var(--color-accent-primary, #c0a46c)"
                  stroke-width="3"
                />
              </svg>
              <span class="ac-mini-value">{{ (charactersStore.byPlayer(player.id)[0] as any).armor_class }}</span>
            </span>
          </div>
        </div>

        <!-- Dropdown trigger for non-GM players -->
        <div v-if="!player.is_gm" class="player-actions">
          <button
            class="action-trigger"
            @click.stop="toggleDropdown(player.id)"
          >
            <MoreVertical :size="16" />
          </button>

          <div
            v-if="openDropdownId === player.id"
            class="dropdown-menu"
          >
            <button class="dropdown-item" disabled>
              <Info :size="14" />
              <span>Информация</span>
            </button>
            <button class="dropdown-item" disabled>
              <Backpack :size="14" />
              <span>Инвентарь</span>
            </button>
            <button
              :class="['dropdown-item', { active: player.can_move }]"
              @click="handleToggleMovement(player.id)"
            >
              <Move :size="14" />
              <span>Движение</span>
              <Check v-if="player.can_move" :size="14" class="check-mark" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { MoreVertical, Info, Backpack, Move, Check } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { sessionApi } from '@/services/api'

const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()

const openDropdownId = ref<number | null>(null)

function playerAvatar(playerId: number): string | null {
  const chars = charactersStore.byPlayer(playerId)
  if (chars.length > 0 && chars[0].avatar_url) {
    return chars[0].avatar_url
  }
  return null
}

function toggleDropdown(playerId: number) {
  openDropdownId.value = openDropdownId.value === playerId ? null : playerId
}

function closeDropdown() {
  openDropdownId.value = null
}

async function handleToggleMovement(playerId: number) {
  try {
    const result = await sessionApi.toggleMovement(playerId)
    // Optimistic update (WS will also update, but this is faster)
    const player = sessionStore.players.find(p => p.id === playerId)
    if (player) {
      player.can_move = result.can_move
    }
  } catch (error) {
    console.error('Failed to toggle movement:', error)
  }
  openDropdownId.value = null
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.player-actions')) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.players-tab {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  padding: var(--spacing-8);
}

.players-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.player-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--radius-md);
  background: var(--color-bg-elevated);
  transition: all var(--duration-fast);
}

.player-item:hover {
  background: var(--alpha-overlay-light);
}

.player-item.is-gm {
  border-left: 3px solid var(--color-accent-gold);
}

.player-status {
  display: flex;
  align-items: center;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--color-text-muted);
}

.status-dot.online {
  background: var(--color-success);
}

.player-avatar-slot {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  overflow: hidden;
  flex-shrink: 0;
}

.player-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.player-avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: var(--color-accent-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.player-info {
  flex: 1;
  min-width: 0;
}

.player-name {
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-1);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.gm-badge {
  font-size: var(--font-size-xs);
  padding: 2px 6px;
  background: var(--color-accent-gold);
  color: var(--color-text-inverse);
  border-radius: var(--radius-sm);
  font-weight: var(--font-weight-bold);
}

.move-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: var(--radius-full);
  background: var(--color-success);
  color: white;
}

.player-characters {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.ac-mini {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 26px;
  flex-shrink: 0;
}

.ac-mini-svg {
  position: absolute;
  width: 100%;
  height: 100%;
}

.ac-mini-value {
  position: relative;
  font-family: var(--font-family-display);
  font-size: 9px;
  font-weight: 700;
  color: var(--color-accent-primary, #c0a46c);
  line-height: 1;
  margin-top: -1px;
}

/* Dropdown */
.player-actions {
  position: relative;
}

.action-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.action-trigger:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: var(--spacing-1);
  min-width: 180px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--alpha-overlay-medium);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 100;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.dropdown-item:hover:not(:disabled) {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.dropdown-item:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.dropdown-item.active {
  color: var(--color-success);
}

.check-mark {
  margin-left: auto;
  color: var(--color-success);
}
</style>
