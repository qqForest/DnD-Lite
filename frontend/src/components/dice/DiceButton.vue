<template>
  <button
    :class="['dice-btn', { active: isActive }]"
    @click="$emit('select')"
  >
    <span class="dice-icon">🎲</span>
    <span class="dice-label">{{ type }}</span>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  type: string
  isActive?: boolean
}>()

defineEmits<{
  select: []
}>()
</script>

<style scoped>
.dice-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-3) var(--spacing-2);
  background: var(--color-bg-elevated);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  min-width: 64px;
  cursor: pointer;
  transition: all var(--duration-fast);
  color: var(--color-text-primary);
}

.dice-btn:hover {
  background: var(--alpha-overlay-medium);
  transform: translateY(-2px);
}

.dice-btn.active {
  border-color: var(--color-accent-primary);
  background: var(--color-bg-elevated);
  box-shadow: 0 0 20px rgba(233, 69, 96, 0.4);
}

.dice-icon {
  font-size: var(--font-size-2xl);
  filter: grayscale(100%);
  transition: filter var(--duration-fast);
}

.dice-btn.active .dice-icon,
.dice-btn:hover .dice-icon {
  filter: grayscale(0%);
}

.dice-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  font-family: var(--font-family-mono);
}
</style>
