<template>
  <div class="profile-topbar">
    <button class="menu-btn" @click="emit('toggleSidebar')">
      <Menu :size="22" />
    </button>
    <h1 class="topbar-title">Профиль</h1>
  </div>
</template>

<script setup lang="ts">
import { Menu } from 'lucide-vue-next'

const emit = defineEmits<{
  toggleSidebar: []
}>()
</script>

<style scoped>
.profile-topbar {
  height: 48px;
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: 0 var(--spacing-4);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
  flex-shrink: 0;
  cursor: pointer;
  border: none;
  background: none;
}

.menu-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.topbar-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}
</style>
