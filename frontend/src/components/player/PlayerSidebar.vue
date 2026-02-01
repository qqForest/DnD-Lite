<template>
  <Teleport to="body">
    <Transition name="sidebar">
      <div v-if="modelValue" class="sidebar-overlay" @click="close">
        <div class="sidebar" @click.stop>
          <div class="sidebar-header">
            <h2>Меню</h2>
            <button class="close-btn" @click="close">×</button>
          </div>

          <div class="sidebar-content">
            <!-- Информация о сессии -->
            <div class="section">
              <h3>Информация о сессии</h3>
              <div class="info-item">
                <span class="label">Код сессии:</span>
                <span class="value">{{ sessionStore.code }}</span>
              </div>
              <div class="info-item">
                <span class="label">Игроков в сессии:</span>
                <span class="value">{{ sessionStore.sessionState?.player_count || 0 }}</span>
              </div>
              <div class="info-item">
                <span class="label">Статус:</span>
                <span v-if="sessionStore.sessionStarted" class="status-badge started">
                  Игра начата
                </span>
                <span v-else class="status-badge waiting">
                  Ожидание начала
                </span>
              </div>
            </div>

            <!-- Дополнительные пункты меню можно добавить позже -->
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useSessionStore } from '@/stores/session'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const sessionStore = useSessionStore()

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: var(--alpha-overlay-heavy);
  z-index: var(--z-modal);
  backdrop-filter: blur(4px);
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  width: min(90vw, 400px);
  background: var(--color-bg-elevated);
  box-shadow: var(--shadow-2xl);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--alpha-overlay-light);
}

.sidebar-header h2 {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: var(--font-size-2xl);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
}

.close-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-4);
}

.section {
  margin-bottom: var(--spacing-6);
}

.section h3 {
  margin: 0 0 var(--spacing-3) 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-3);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-2);
}

.info-item .label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.info-item .value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  font-family: var(--font-family-mono);
}

.status-badge {
  display: inline-block;
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.status-badge.started {
  background: var(--color-success);
  color: var(--color-text-inverse);
}

.status-badge.waiting {
  background: var(--color-warning);
  color: var(--color-text-inverse);
}

/* Transitions */
.sidebar-enter-active,
.sidebar-leave-active {
  transition: opacity var(--duration-normal) var(--ease-out);
}

.sidebar-enter-active .sidebar,
.sidebar-leave-active .sidebar {
  transition: transform var(--duration-normal) var(--ease-out);
}

.sidebar-enter-from,
.sidebar-leave-to {
  opacity: 0;
}

.sidebar-enter-from .sidebar,
.sidebar-leave-to .sidebar {
  transform: translateX(-100%);
}
</style>
