<template>
  <div class="left-panel">
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <component :is="tab.icon" :size="24" />
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>
    <div class="tab-content">
      <PlayersTab v-if="activeTab === 'players'" />
      <div v-else-if="activeTab === 'events'" class="placeholder">
        Журнал событий (скоро)
      </div>
      <CombatTab v-else-if="activeTab === 'combat'" />
      <div v-else-if="activeTab === 'stats'" class="placeholder">
        Статистика (скоро)
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Users, ScrollText, Swords, BarChart3 } from 'lucide-vue-next'
import PlayersTab from './PlayersTab.vue'
import CombatTab from './CombatTab.vue'

const activeTab = ref<'players' | 'events' | 'combat' | 'stats'>('players')

const tabs = [
  { id: 'players' as const, label: 'Игроки', icon: Users },
  { id: 'events' as const, label: 'События', icon: ScrollText },
  { id: 'combat' as const, label: 'Бой', icon: Swords },
  { id: 'stats' as const, label: 'Статистика', icon: BarChart3 }
]
</script>

<style scoped>
.left-panel {
  display: flex;
  flex-direction: column;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--alpha-overlay-light);
  overflow: hidden;
  width: 100%;
  height: 100%;
}

.tabs {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-2);
  gap: var(--spacing-1);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
  min-height: 44px;
}

.tab-button:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.tab-button.active {
  background: var(--alpha-overlay-medium);
  color: var(--color-accent-primary);
}

.tab-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-4);
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}
</style>
