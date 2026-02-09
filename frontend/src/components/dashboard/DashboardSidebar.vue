<template>
  <Teleport to="body">
    <Transition name="sidebar">
      <div v-if="modelValue" class="sidebar-overlay" @click="close">
        <div class="sidebar" @click.stop>
          <div class="sidebar-header">
            <h2>Меню</h2>
            <button class="close-btn" @click="close">&times;</button>
          </div>

          <div class="sidebar-content">
            <div class="user-section">
              <span class="display-name">{{ authStore.user?.display_name }}</span>
              <span class="role-badge">{{ roleLabel }}</span>
            </div>

            <nav class="sidebar-nav">
              <button class="nav-btn" @click="goProfile">
                <UserCircle :size="20" />
                <span>Мой профиль</span>
              </button>
              <button class="nav-btn nav-btn--danger" @click="handleLogout">
                <LogOut :size="20" />
                <span>Выйти</span>
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
import { useRouter } from 'vue-router'
import { UserCircle, LogOut } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useSessionStore } from '@/stores/session'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const router = useRouter()
const authStore = useAuthStore()
const sessionStore = useSessionStore()

const roleLabel = computed(() => {
  const role = authStore.user?.role || 'player'
  switch (role) {
    case 'player': return 'Игрок'
    case 'gm': return 'Game Master'
    case 'both': return 'Игрок / GM'
    default: return role
  }
})

function close() {
  emit('update:modelValue', false)
}

function goProfile() {
  close()
  router.push({ name: 'profile' })
}

function handleLogout() {
  close()
  authStore.logout()
  sessionStore.clearSession()
  router.push({ name: 'login' })
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

.user-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-6);
}

.display-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.role-badge {
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #fff;
  font-weight: 500;
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
