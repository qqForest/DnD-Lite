<template>
  <div class="roll-history">
    <div class="history-header">
      <h4>История бросков</h4>
      <button v-if="diceStore.history.length > 0" class="clear-btn" @click="clearHistory">
        Очистить
      </button>
    </div>
    <div v-if="diceStore.history.length === 0" class="empty-state">
      <p>Пока нет бросков</p>
    </div>
    <div v-else class="history-list">
      <div
        v-for="(result, index) in recentRolls"
        :key="index"
        class="history-item"
      >
        <div class="item-header">
          <span class="player-name">{{ result.player_name }}</span>
          <span class="timestamp">{{ formatTime(result.timestamp) }}</span>
        </div>
        <div class="item-result">
          <span class="formula">{{ result.formula }}</span>
          <span class="total">= {{ result.total }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDiceStore } from '@/stores/dice'

const diceStore = useDiceStore()

const recentRolls = computed(() => {
  return diceStore.history.slice(-10).reverse()
})

function formatTime(timestamp?: string): string {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function clearHistory() {
  diceStore.clearHistory()
}
</script>

<style scoped>
.roll-history {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  max-height: 400px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h4 {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.clear-btn {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast);
}

.clear-btn:hover {
  color: var(--color-text-primary);
  background: var(--alpha-overlay-light);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-6);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  overflow-y: auto;
}

.history-item {
  padding: var(--spacing-3);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-accent-primary);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-1);
}

.player-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.timestamp {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-family: var(--font-family-mono);
}

.item-result {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.formula {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.total {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent-primary);
}
</style>
