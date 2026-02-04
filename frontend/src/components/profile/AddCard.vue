<template>
  <div class="add-card" @click="$emit('click')">
    <span class="add-icon">+</span>
    <span class="add-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
}>()

defineEmits<{
  click: []
}>()
</script>

<style scoped>
.add-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-6);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
  min-height: 160px;
}

.add-card:hover {
  border-color: var(--color-primary);
  background-color: var(--color-bg-secondary);
}

.add-icon {
  font-size: 2rem;
  color: var(--color-text-secondary);
  line-height: 1;
}

.add-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
</style>
