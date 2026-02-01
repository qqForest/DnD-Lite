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
        <div class="player-info">
          <div class="player-name">
            {{ player.name }}
            <span v-if="player.is_gm" class="gm-badge">GM</span>
          </div>
          <div v-if="charactersStore.byPlayer(player.id).length > 0" class="player-characters">
            {{ charactersStore.byPlayer(player.id).length }} персонаж(ей)
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'

const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
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

.player-characters {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}
</style>
