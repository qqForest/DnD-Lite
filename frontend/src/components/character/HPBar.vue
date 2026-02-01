<template>
  <div class="hp-bar">
    <div class="hp-bar-track">
      <div
        class="hp-bar-fill"
        :class="hpState"
        :style="{ width: `${percentage}%` }"
      />
    </div>
    <span class="hp-bar-text">{{ current }}/{{ max }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  current: number
  max: number
}>()

const percentage = computed(() => (props.current / props.max) * 100)

const hpState = computed(() => {
  if (percentage.value > 50) return 'hp-healthy'
  if (percentage.value > 25) return 'hp-wounded'
  return 'hp-critical'
})
</script>

<style scoped>
.hp-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.hp-bar-track {
  flex: 1;
  height: 8px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.hp-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-normal) var(--ease-out);
}

.hp-healthy {
  background: var(--color-success);
}

.hp-wounded {
  background: var(--color-warning);
}

.hp-critical {
  background: var(--color-danger);
  animation: pulse 1s infinite;
}

.hp-bar-text {
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono);
  min-width: 60px;
  text-align: right;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
</style>
