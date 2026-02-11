<template>
  <div class="dashboard-view">
    <DashboardTopBar @toggle-sidebar="showSidebar = !showSidebar" />
    <DashboardSidebar v-model="showSidebar" />

    <div class="content">
      <!-- Logo -->
      <h1 class="logo">DnD Lite</h1>

      <!-- User card -->
      <div class="user-card">
        <div class="user-info">
          <span class="user-name">{{ authStore.user?.display_name }}</span>
          <span class="role-badge">{{ roleLabel }}</span>
        </div>
        <BaseButton variant="secondary" size="lg" class="full-btn" @click="router.push({ name: 'profile' })">
          <UserCircle :size="20" />
          Мой профиль
        </BaseButton>
      </div>

      <!-- Quick actions -->
      <div class="actions">
        <BaseButton
          v-if="isPlayer"
          variant="primary"
          size="lg"
          class="full-btn"
          @click="router.push({ name: 'join' })"
        >
          <Zap :size="20" />
          Быстрое подключение
        </BaseButton>
        <BaseButton
          v-if="isGm"
          variant="primary"
          size="lg"
          class="full-btn"
          :disabled="loading"
          @click="showCreateModal = true"
        >
          <Dice6 :size="20" />
          Создать сессию
        </BaseButton>
      </div>

      <!-- Stats -->
      <section v-if="stats" class="stats-section">
        <h2 class="section-title">Статистика</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-number">{{ stats.total_sessions }}</span>
            <span class="stat-label">Сессий</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ stats.total_characters }}</span>
            <span class="stat-label">Персонажей</span>
          </div>
          <div v-if="isGm" class="stat-card">
            <span class="stat-number">{{ stats.total_npcs }}</span>
            <span class="stat-label">NPC</span>
          </div>
        </div>
      </section>
      <div v-else-if="statsLoading" class="stats-loading">
        Загрузка статистики...
      </div>

      <!-- Top characters -->
      <section v-if="isPlayer && stats?.top_characters?.length" class="top-section">
        <h2 class="section-title">Лучшие персонажи</h2>
        <div class="top-characters">
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
      </section>
      <section v-else-if="isPlayer && stats && stats.top_characters.length === 0" class="empty-state">
        <p>Статистика появится после участия в сессиях.</p>
        <p class="hint">Создайте персонажа и присоединитесь к игре!</p>
      </section>
    </div>

    <CreateSessionModal
      v-model="showCreateModal"
      @create="handleCreateSession"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/services/api'
import type { UserStats } from '@/types/models'
import { Zap, Dice6, UserCircle } from 'lucide-vue-next'
import BaseButton from '@/components/common/BaseButton.vue'
import CreateSessionModal from '@/components/gm/CreateSessionModal.vue'
import DashboardTopBar from '@/components/dashboard/DashboardTopBar.vue'
import DashboardSidebar from '@/components/dashboard/DashboardSidebar.vue'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const sessionStore = useSessionStore()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(false)
const showCreateModal = ref(false)
const showSidebar = ref(false)
const stats = ref<UserStats | null>(null)
const statsLoading = ref(true)

const role = computed(() => authStore.user?.role || 'player')
const isPlayer = computed(() => role.value === 'player' || role.value === 'both')
const isGm = computed(() => role.value === 'gm' || role.value === 'both')

const roleLabel = computed(() => {
  switch (role.value) {
    case 'player': return 'Игрок'
    case 'gm': return 'Game Master'
    case 'both': return 'Игрок / GM'
    default: return role.value
  }
})

async function handleCreateSession(userMapId?: string) {
  loading.value = true
  showCreateModal.value = false
  try {
    await sessionStore.createSession(userMapId)
    router.push({
      name: 'gm-lobby-with-code',
      params: { code: sessionStore.code }
    })
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
  min-height: 100dvh;
  background: var(--color-bg-primary);
}

.content {
  padding: var(--spacing-6) var(--spacing-4);
  max-width: 480px;
  margin: 0 auto;
}

.logo {
  text-align: center;
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-6);
}

/* User card */
.user-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-3);
}

.user-name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.role-badge {
  font-size: var(--font-size-xs);
  padding: 2px 10px;
  border-radius: var(--radius-full, 999px);
  background: var(--color-accent-primary, var(--color-primary));
  color: #fff;
  font-weight: 500;
}

/* Actions */
.actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-8);
}

.full-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
}

/* Stats */
.stats-section {
  margin-bottom: var(--spacing-8);
}

.section-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-4);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: var(--spacing-3);
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
}

.stat-number {
  font-family: var(--font-family-display);
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-accent-primary, var(--color-primary));
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
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.top-rank {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-accent-primary, var(--color-primary));
  min-width: 32px;
}

.top-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-name {
  font-family: var(--font-family-display);
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
  font-family: var(--font-family-display);
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
