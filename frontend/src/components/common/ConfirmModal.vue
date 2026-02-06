<template>
  <BaseModal :model-value="modelValue" :title="title" size="sm" @update:model-value="$emit('update:modelValue', $event)">
    <p class="confirm-message">{{ message }}</p>
    <template #footer>
      <div class="confirm-actions">
        <BaseButton :variant="danger ? 'danger' : 'primary'" size="lg" class="confirm-btn" @click="$emit('confirm')">
          {{ confirmText }}
        </BaseButton>
        <BaseButton variant="ghost" size="lg" class="cancel-btn" @click="$emit('update:modelValue', false)">
          Отмена
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import BaseModal from './BaseModal.vue'
import BaseButton from './BaseButton.vue'

withDefaults(defineProps<{
  modelValue: boolean
  title: string
  message: string
  confirmText?: string
  danger?: boolean
}>(), {
  confirmText: 'Удалить',
  danger: true
})

defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
}>()
</script>

<style scoped>
.confirm-message {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin: 0;
}

.confirm-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
}

.confirm-btn,
.cancel-btn {
  width: 100%;
  max-width: 300px;
  min-height: 48px;
}
</style>
