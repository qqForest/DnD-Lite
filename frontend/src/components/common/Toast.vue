<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
      >
        <div class="toast-content">
          <component v-if="toast.icon" :is="toast.icon" :size="20" />
          <span class="toast-message">{{ toast.message }}</span>
        </div>
        <button class="toast-close" @click="removeToast(toast.id)">
          <X :size="16" />
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { X, CheckCircle, AlertCircle, Info } from 'lucide-vue-next'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
  icon?: any
  duration?: number
}

const toasts = ref<Toast[]>([])

let toastIdCounter = 0

function addToast(message: string, type: Toast['type'] = 'info', duration = 3000) {
  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info
  }

  const toast: Toast = {
    id: toastIdCounter++,
    message,
    type,
    icon: icons[type],
    duration
  }

  toasts.value.push(toast)

  if (duration > 0) {
    setTimeout(() => {
      removeToast(toast.id)
    }, duration)
  }
}

function removeToast(id: number) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// Экспортируем функции для использования в composable
onMounted(() => {
  ;(window as any).__toast = {
    success: (message: string, duration?: number) => addToast(message, 'success', duration),
    error: (message: string, duration?: number) => addToast(message, 'error', duration),
    info: (message: string, duration?: number) => addToast(message, 'info', duration)
  }
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: var(--spacing-4);
  right: var(--spacing-4);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  border-left: 3px solid var(--color-accent-primary);
  min-width: 300px;
}

.toast-success {
  border-left-color: var(--color-success);
}

.toast-error {
  border-left-color: var(--color-danger);
}

.toast-info {
  border-left-color: var(--color-info);
}

.toast-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  flex: 1;
}

.toast-message {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.toast-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
  flex-shrink: 0;
}

.toast-close:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.toast-enter-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.toast-leave-active {
  transition: all var(--duration-normal) var(--ease-in);
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
