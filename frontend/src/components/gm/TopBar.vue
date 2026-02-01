<template>
  <div class="top-bar">
    <div class="logo">
      <h1>DnD Lite GM</h1>
    </div>
    <div class="session-info">
      <span v-if="sessionStore.code" class="session-code">
        Сессия: {{ sessionStore.code }}
      </span>
      <span v-if="sessionStore.players.length > 0" class="player-count">
        Игроков: {{ sessionStore.players.length }}
      </span>
      <span v-if="sessionStore.isConnected" class="connection-status connected">
        ●
      </span>
      <span v-else class="connection-status disconnected">
        ○
      </span>
    </div>
    <div class="actions">
      <button class="action-button" title="Настройки">
        <Settings :size="20" />
      </button>
      <button class="action-button" title="Помощь">
        <HelpCircle :size="20" />
      </button>
      <button class="action-button" title="Профиль">
        <User :size="20" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Settings, HelpCircle, User } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()
</script>

<style scoped>
.top-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: 0 var(--spacing-4);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--alpha-overlay-light);
  width: 100%;
  height: 100%;
}


.logo h1 {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text-primary);
}

.session-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  margin-left: auto;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.session-code {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-medium);
}

.connection-status {
  font-size: var(--font-size-lg);
}

.connection-status.connected {
  color: var(--color-success);
}

.connection-status.disconnected {
  color: var(--color-text-muted);
}

.actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
}

.action-button:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}
</style>
