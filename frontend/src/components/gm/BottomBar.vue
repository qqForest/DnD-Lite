<template>
  <div class="bottom-bar">
    <BaseButton variant="primary" size="lg" @click="showDiceModal = true">
      <Dice6 :size="20" />
      Бросок
    </BaseButton>

    <div class="roll-history">
      <div
        v-for="(roll, index) in recentRolls"
        :key="index"
        class="roll-item"
        @click="showRollDetails(roll)"
      >
        <span class="roll-player">{{ roll.player_name }}</span>
        <span class="roll-notation">{{ roll.formula }}</span>
        <span class="roll-result">{{ roll.total }}</span>
      </div>
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
import type { DiceResult } from '@/types/models'

const diceStore = useDiceStore()
const showDiceModal = ref(false)

const recentRolls = computed(() => {
  return diceStore.history.slice(0, 1)
})

function showRollDetails(roll: DiceResult) {
  diceStore.lastResult = roll
  diceStore.showResult = true
}
</script>

<style scoped>
.bottom-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: 0 var(--spacing-4);
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--alpha-overlay-light);
  width: 100%;
  height: 100%;
}

.roll-history {
  display: flex;
  gap: var(--spacing-3);
  margin-left: auto;
  overflow-x: auto;
}

.roll-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
  white-space: nowrap;
}

.roll-item:hover {
  background: var(--alpha-overlay-medium);
  transform: translateY(-2px);
}

.roll-player {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.roll-notation {
  font-family: var(--font-family-mono);
  color: var(--color-text-primary);
}

.roll-result {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent-primary);
}
</style>
