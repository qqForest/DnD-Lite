<template>
  <div class="dashboard-view">
    <div class="container">
      <header class="dashboard-header">
        <div class="header-left">
          <h1 class="title">DnD Lite</h1>
          <span class="greeting">{{ authStore.user?.display_name }}</span>
        </div>
        <div class="header-actions">
          <BaseButton variant="ghost" size="sm" @click="router.push({ name: 'profile' })">
            Мой профиль
          </BaseButton>
          <BaseButton variant="ghost" size="sm" @click="handleLogout">
            Выйти
          </BaseButton>
        </div>
      </header>

      <!-- Quick actions -->
      <section class="quick-actions">
        <BasePanel variant="elevated" class="action-card" v-if="isGm">
          <div class="action-content">
            <h3 class="action-title">Создать сессию</h3>
            <p class="action-desc">Начните новую игровую сессию как Game Master</p>
            <BaseButton variant="primary" :disabled="loading" @click="handleCreateSession">
              Создать
            </BaseButton>
          </div>
        </BasePanel>

        <BasePanel variant="elevated" class="action-card" v-if="isPlayer">
          <div class="action-content">
            <h3 class="action-title">Присоединиться</h3>
            <p class="action-desc">Войдите в существующую сессию по коду комнаты</p>
            <BaseButton variant="primary" @click="router.push({ name: 'join' })">
              Войти в сессию
            </BaseButton>
          </div>
        </BasePanel>

        <BasePanel variant="elevated" class="action-card" v-if="isPlayer">
          <div class="action-content">
            <h3 class="action-title">Новый персонаж</h3>
            <p class="action-desc">Создайте персонажа для будущих сессий</p>
            <BaseButton variant="secondary" @click="router.push({ name: 'create-character' })">
              Создать
            </BaseButton>
          </div>
        </BasePanel>
      </section>

      <!-- Stats overview -->
      <section class="stats-section">
        <h2 class="section-title">Обзор</h2>
        <div class="stats-grid" v-if="stats">
          <div class="stat-card">
            <span class="stat-number">{{ stats.total_sessions }}</span>
            <span class="stat-label">Сессий сыграно</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ stats.total_characters }}</span>
            <span class="stat-label">Персонажей</span>
          </div>
          <div class="stat-card" v-if="isGm">
            <span class="stat-number">{{ stats.total_npcs }}</span>
            <span class="stat-label">NPC</span>
          </div>
        </div>
        <div v-else-if="statsLoading" class="stats-loading">
          Загрузка статистики...
        </div>
      </section>

      <!-- Top characters -->
      <section class="top-section" v-if="isPlayer">
        <h2 class="section-title">Самые играемые персонажи</h2>
        <div v-if="stats && stats.top_characters.length > 0" class="top-characters">
          <div
            v-for="(char, index) in stats.top_characters"
            :key="char.id"
            class="top-character-row"
          >
            <span class="top-rank">#{{ index + 1 }}</span>
            <div class="top-info">
              <span class="top-name">{{ char.name }}</span>
              <span class="top-class" v-if="char.class_name">{{ char.class_name }} &middot; Ур. {{ char.level }}</span>
            </div>
            <div class="top-sessions">
              <span class="sessions-count">{{ char.sessions_played }}</span>
              <span class="sessions-label">{{ pluralizeSessions(char.sessions_played) }}</span>
            </div>
          </div>
        </div>
        <div v-else-if="stats && stats.top_characters.length === 0" class="empty-state">
          <p>Статистика появится после участия в сессиях.</p>
          <p class="hint">Создайте персонажа и присоединитесь к игре!</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/services/api'
import type { UserStats } from '@/types/models'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const sessionStore = useSessionStore()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(false)
const stats = ref<UserStats | null>(null)
const statsLoading = ref(true)

const role = computed(() => authStore.user?.role || 'player')
const isPlayer = computed(() => role.value === 'player' || role.value === 'both')
const isGm = computed(() => role.value === 'gm' || role.value === 'both')

function handleLogout() {
  authStore.logout()
  sessionStore.clearSession()
  router.push({ name: 'login' })
}

async function handleCreateSession() {
  loading.value = true
  try {
    await sessionStore.createSession()
    router.push({ name: 'gm-lobby' })
  } catch (error) {
    console.error('Failed to create session:', error)
    toast.error('Не удалось создать сессию')
  } finally {
    loading.value = false
  }
}

function pluralizeSessions(n: number): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return 'сессия'
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return 'сессии'
  return 'сессий'
}

onMounted(async () => {
  statsLoading.value = true
  try {
    stats.value = await authApi.getStats()
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    statsLoading.value = false
  }
})
</script>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  padding: var(--spacing-6);
  background: var(--color-bg-primary);
}

.container {
  max-width: 960px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-8);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-3);
}

.title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.greeting {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-2);
}

/* Quick actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-8);
}

.action-card {
  width: 100%;
}

.action-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.action-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.action-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Stats */
.stats-section {
  margin-bottom: var(--spacing-8);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-4);
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-5);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.stat-number {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stats-loading {
  text-align: center;
  padding: var(--spacing-6);
  color: var(--color-text-secondary);
}

/* Top characters */
.top-section {
  margin-bottom: var(--spacing-8);
}

.top-characters {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.top-character-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.top-rank {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
  min-width: 32px;
}

.top-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.top-class {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.top-sessions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.sessions-count {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.sessions-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-6);
  color: var(--color-text-secondary);
}

.empty-state p {
  margin: 0;
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-top: var(--spacing-2) !important;
}
</style>
