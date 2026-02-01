<template>
  <div :class="['panel', `panel-${variant}`]">
    <header v-if="$slots.header || title" class="panel-header">
      <slot name="header">
        <h3 class="panel-title">{{ title }}</h3>
      </slot>
    </header>
    <div class="panel-content">
      <slot />
    </div>
    <footer v-if="$slots.footer" class="panel-footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'default' | 'glass' | 'elevated' | 'flat'
  title?: string
}>()
</script>

<style scoped>
.panel {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.panel-glass {
  background: var(--alpha-glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--alpha-overlay-medium);
}

.panel-elevated {
  background: var(--color-bg-elevated);
  box-shadow: var(--shadow-lg);
}

.panel-flat {
  background: transparent;
}

.panel-header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--alpha-overlay-light);
}

.panel-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.panel-content {
  padding: var(--spacing-4);
}

.panel-footer {
  padding: var(--spacing-3) var(--spacing-4);
  border-top: 1px solid var(--alpha-overlay-light);
  background: var(--alpha-overlay-light);
}
</style>
