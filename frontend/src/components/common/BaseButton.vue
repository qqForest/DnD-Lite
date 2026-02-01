<template>
  <button
    :class="['btn', `btn-${variant}`, `btn-${size}`, { 'btn-icon-only': iconOnly }]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <span v-if="icon" class="btn-icon">
      <component :is="icon" />
    </span>
    <span v-if="!iconOnly" class="btn-text">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  icon?: Component
  iconOnly?: boolean
  disabled?: boolean
}>()

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-family-primary);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.btn-sm {
  padding: 6px 12px;
  font-size: var(--font-size-sm);
  min-height: 32px;
}

.btn-md {
  padding: 8px 16px;
  font-size: var(--font-size-base);
  min-height: 40px;
}

.btn-lg {
  padding: 12px 24px;
  font-size: var(--font-size-lg);
  min-height: 48px;
}

.btn-primary {
  background: var(--color-accent-primary);
  color: var(--color-text-primary);
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.1);
  box-shadow: var(--glow-accent);
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--alpha-overlay-medium);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--alpha-overlay-light);
  border-color: var(--color-accent-primary);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.btn-danger {
  background: var(--color-danger);
  color: var(--color-text-primary);
}

.btn-danger:hover:not(:disabled) {
  filter: brightness(1.1);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon-only {
  aspect-ratio: 1;
  padding: var(--spacing-2);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
