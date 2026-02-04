<template>
  <div class="player-topbar">
    <button class="menu-btn" @click="emit('toggleSidebar')">
      <Menu :size="20" />
    </button>

    <div class="topbar-content">
      <div class="session-info">
        <span class="session-code">{{ sessionStore.code || '—' }}</span>
      </div>

      <div class="connection-status" :class="{ connected: sessionStore.isConnected }">
        <span class="status-dot"></span>
        <span>{{ sessionStore.isConnected ? 'Подключено' : 'Отключено' }}</span>
      </div>

      <div class="player-info">
        <span class="player-name">{{ currentPlayerName }}</span>
        <button class="leave-btn" title="Покинуть сессию" @click="emit('leave')">
          <LogOut :size="18" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Menu, LogOut } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'

const emit = defineEmits<{
  toggleSidebar: []
  leave: []
}>()

const sessionStore = useSessionStore()

const currentPlayerName = computed(() => {
  if (sessionStore.currentPlayer) {
    return sessionStore.currentPlayer.name
  }
  return '—'
})
</script>

<style scoped>
.player-topbar {
  height: 100%;
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: 0 var(--spacing-4);
  background: var(--color-bg-secondary);
}

.menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
  flex-shrink: 0;
  cursor: pointer;
}

.menu-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.topbar-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
  font-size: var(--font-size-sm);
}

.session-info,
.player-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.session-label,
.player-label {
  color: var(--color-text-secondary);
}

.session-code {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-semibold);
  color: var(--color-accent-primary);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  color: var(--color-text-muted);
}

.connection-status.connected {
  color: var(--color-success);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  display: inline-block;
}

.player-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.leave-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.leave-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-danger, #ef4444);
}

@media (max-width: 768px) {
  .topbar-content {
    font-size: var(--font-size-xs);
    gap: var(--spacing-2);
  }

  .session-label,
  .player-label {
    display: none;
  }
}
</style>
