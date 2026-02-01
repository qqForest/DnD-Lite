<template>
  <div class="player-dice-selector">
    <BaseButton variant="primary" size="lg" @click="showDiceModal = true">
      <Dice6 :size="20" />
      Бросок
    </BaseButton>

    <div v-if="lastResult" class="last-result" @click="showRollDetails">
      <span class="result-label">Последний бросок:</span>
      <span class="result-value">{{ lastResult.total }}</span>
      <span class="result-notation">({{ lastResult.formula }})</span>
    </div>

    <DiceRollModal v-model="showDiceModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Dice6 } from 'lucide-vue-next'
import { useDiceStore } from '@/stores/dice'
import BaseButton from '@/components/common/BaseButton.vue'
import DiceRollModal from '@/components/dice/DiceRollModal.vue'

const diceStore = useDiceStore()
const showDiceModal = ref(false)

const lastResult = computed(() => diceStore.lastResult)

function showRollDetails() {
  if (lastResult.value) {
    diceStore.showResult = true
  }
}
</script>

<style scoped>
.player-dice-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
}

.last-result {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
  margin-left: auto;
}

.last-result:hover {
  background: var(--alpha-overlay-medium);
  transform: translateY(-2px);
}

.result-label {
  color: var(--color-text-secondary);
}

.result-value {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent-primary);
}

.result-notation {
  font-family: var(--font-family-mono);
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

@media (max-width: 768px) {
  .player-dice-selector {
    padding: var(--spacing-2) var(--spacing-3);
  }

  .result-label {
    display: none;
  }
}
</style>
