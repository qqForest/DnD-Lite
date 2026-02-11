<template>
  <div v-if="combatStore.isActive && sortedEntries.length > 0" class="initiative-bar">
    <div class="initiative-label">
      <Swords :size="16" />
      <span>Порядок инициативы</span>
    </div>
    
    <div class="initiative-cards">
      <TransitionGroup name="card" tag="div" class="cards-container">
        <div
          v-for="(entry, index) in sortedEntries"
          :key="entry.is_npc ? `npc-${entry.character_id}` : `player-${entry.player_id}`"
          :class="['initiative-card', {
            'no-roll': entry.roll === null,
            'is-npc': entry.is_npc
          }]"
        >
          <div class="card-rank">
            <span v-if="index === 0 && entry.roll !== null" class="medal">🥇</span>
            <span v-else-if="index === 1 && entry.roll !== null" class="medal">🥈</span>
            <span v-else-if="index === 2 && entry.roll !== null" class="medal">🥉</span>
            <span v-else class="rank-number">{{ entry.roll !== null ? index + 1 : '—' }}</span>
          </div>

          <div class="card-info">
            <div class="character-name">
              {{ entry.character_name || entry.player_name }}
              <span v-if="entry.is_npc" class="npc-badge">NPC</span>
            </div>
            <div v-if="entry.character_name && !entry.is_npc" class="player-name">{{ entry.player_name }}</div>
          </div>

          <div class="card-roll">
            <span v-if="entry.roll !== null" class="roll-value">{{ entry.roll }}</span>
            <span v-else class="roll-pending">?</span>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Swords } from 'lucide-vue-next'
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
.initiative-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--alpha-overlay-light);
  overflow-x: auto;
  overflow-y: hidden;
}

.initiative-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  white-space: nowrap;
  flex-shrink: 0;
}

.initiative-cards {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
}

.cards-container {
  display: flex;
  gap: var(--spacing-3);
  padding: var(--spacing-1) 0;
}

.initiative-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  min-width: 160px;
  flex-shrink: 0;
  transition: all var(--duration-fast);
  box-shadow: var(--shadow-sm);
}

.initiative-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.initiative-card.no-roll {
  opacity: 0.6;
}

.initiative-card.is-npc {
  border-left: 3px solid var(--color-danger);
}

.card-rank {
  width: 28px;
  text-align: center;
  flex-shrink: 0;
}

.medal {
  font-size: var(--font-size-lg);
}

.rank-number {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-tertiary);
}

.card-info {
  flex: 1;
  min-width: 0;
}

.character-name {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.npc-badge {
  font-size: var(--font-size-xs);
  padding: 2px 6px;
  background: var(--color-danger);
  color: white;
  border-radius: var(--radius-sm);
  font-weight: var(--font-weight-normal);
  flex-shrink: 0;
}

.player-name {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-roll {
  width: 32px;
  text-align: center;
  flex-shrink: 0;
}

.roll-value {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.roll-pending {
  font-size: var(--font-size-lg);
  color: var(--color-text-tertiary);
}

/* Card transition animations */
.card-enter-active,
.card-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.card-enter-from {
  opacity: 0;
  transform: translateX(-20px) scale(0.9);
}

.card-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.9);
}

.card-move {
  transition: transform var(--duration-normal) var(--ease-out);
}

/* Scrollbar styling */
.initiative-bar::-webkit-scrollbar,
.initiative-cards::-webkit-scrollbar {
  height: 6px;
}

.initiative-bar::-webkit-scrollbar-track,
.initiative-cards::-webkit-scrollbar-track {
  background: transparent;
}

.initiative-bar::-webkit-scrollbar-thumb,
.initiative-cards::-webkit-scrollbar-thumb {
  background: var(--alpha-overlay-medium);
  border-radius: var(--radius-full);
}

.initiative-bar::-webkit-scrollbar-thumb:hover,
.initiative-cards::-webkit-scrollbar-thumb:hover {
  background: var(--alpha-overlay-heavy);
}
</style>
