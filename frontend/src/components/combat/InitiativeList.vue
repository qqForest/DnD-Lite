<template>
  <div class="initiative-list">
    <div class="list-header">
      <h3>Порядок инициативы</h3>
    </div>

    <div class="list-content">
      <TransitionGroup name="list" tag="div" class="entries">
        <div
          v-for="(entry, index) in sortedEntries"
          :key="entry.player_id"
          :class="['initiative-entry', { 'no-roll': entry.roll === null }]"
        >
          <div class="entry-rank">
            <span v-if="index === 0 && entry.roll !== null" class="medal">🥇</span>
            <span v-else-if="index === 1 && entry.roll !== null" class="medal">🥈</span>
            <span v-else-if="index === 2 && entry.roll !== null" class="medal">🥉</span>
            <span v-else class="rank-number">{{ entry.roll !== null ? index + 1 : '-' }}</span>
          </div>

          <div class="entry-info">
            <span class="player-name">{{ entry.character_name || entry.player_name }}</span>
            <span v-if="entry.character_name" class="player-subname">{{ entry.player_name }}</span>
          </div>

          <div class="entry-roll">
            <span v-if="entry.roll !== null" class="roll-value">{{ entry.roll }}</span>
            <span v-else class="roll-pending">—</span>
          </div>
        </div>
      </TransitionGroup>

      <div v-if="sortedEntries.length === 0" class="empty-state">
        <p>Ожидание игроков...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCombatStore } from '@/stores/combat'

const combatStore = useCombatStore()

const sortedEntries = computed(() => {
  return [...combatStore.initiativeList].sort((a, b) => {
    if (a.roll === null && b.roll === null) return 0
    if (a.roll === null) return 1
    if (b.roll === null) return -1
    return b.roll - a.roll
  })
})
</script>

<style scoped>
.initiative-list {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.list-header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--alpha-overlay-light);
}

.list-header h3 {
  margin: 0;
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.list-content {
  padding: var(--spacing-2);
}

.entries {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.initiative-entry {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-md);
  background: var(--alpha-overlay-light);
  transition: all var(--duration-fast);
}

.initiative-entry:hover {
  background: var(--alpha-overlay-medium);
}

.initiative-entry.no-roll {
  opacity: 0.5;
}

.entry-rank {
  width: 32px;
  text-align: center;
}

.medal {
  font-size: var(--font-size-xl);
}

.rank-number {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}

.entry-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.player-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-subname {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.entry-roll {
  width: 40px;
  text-align: right;
}

.roll-value {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.roll-pending {
  font-size: var(--font-size-xl);
  color: var(--color-text-tertiary);
}

.empty-state {
  padding: var(--spacing-8);
  text-align: center;
  color: var(--color-text-tertiary);
}

/* List transition animations */
.list-enter-active,
.list-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.list-move {
  transition: transform var(--duration-normal) var(--ease-out);
}
</style>
