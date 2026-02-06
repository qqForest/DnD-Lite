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
            <div class="status-section">
              <span
                class="status-dot"
                :class="sessionStore.isConnected ? 'connected' : 'disconnected'"
              ></span>
              <span class="status-text">
                {{ sessionStore.isConnected ? 'Подключено' : 'Отключено' }}
              </span>
            </div>

            <div v-if="gm" class="gm-section">
              <span class="section-label">Гейм-мастер</span>
              <div class="gm-name">
                <Crown :size="18" class="gm-icon" />
                <span>{{ gm.name }}</span>
              </div>
            </div>

            <div v-if="otherPlayers.length > 0" class="players-section">
              <span class="section-label">Игроки</span>
              <ul class="players-list">
                <li v-for="p in otherPlayers" :key="p.id" class="player-item">
                  <span
                    class="ready-dot"
                    :class="p.is_ready ? 'ready' : 'not-ready'"
                  ></span>
                  <span class="player-name">{{ p.name }}</span>
                </li>
              </ul>
            </div>

            <nav class="sidebar-nav">
              <button class="nav-btn nav-btn--danger" @click="handleLeave">
                <LogOut :size="20" />
                <span>Покинуть сессию</span>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { LogOut, Crown } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  leave: []
}>()

const sessionStore = useSessionStore()

const gm = computed(() => sessionStore.players.find(p => p.is_gm) ?? null)
const otherPlayers = computed(() => sessionStore.players.filter(p => !p.is_gm))

function close() {
  emit('update:modelValue', false)
}

function handleLeave() {
  close()
  emit('leave')
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
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.close-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: var(--font-size-2xl);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
  border: none;
  background: none;
  cursor: pointer;
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

.status-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-6);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.status-dot.connected {
  background: var(--color-success);
}

.status-dot.disconnected {
  background: var(--color-text-muted);
}

.status-text {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-primary);
}

.gm-section,
.players-section {
  margin-bottom: var(--spacing-4);
}

.section-label {
  display: block;
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2);
}

.gm-name {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.gm-icon {
  color: var(--color-warning, #f59e0b);
  flex-shrink: 0;
}

.players-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.player-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--radius-md);
}

.ready-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.ready-dot.ready {
  background: var(--color-success, #22c55e);
}

.ready-dot.not-ready {
  background: var(--color-text-muted, var(--color-text-secondary));
  opacity: 0.4;
}

.player-name {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  width: 100%;
  min-height: 48px;
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-md);
  background: none;
  border: none;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.nav-btn:hover {
  background: var(--alpha-overlay-light);
}

.nav-btn--danger {
  color: var(--color-danger, #ef4444);
}

.nav-btn--danger:hover {
  background: rgba(239, 68, 68, 0.1);
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
