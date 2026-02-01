<template>
  <div class="home-view">
    <div class="container">
      <h1 class="title">DnD Lite GM</h1>
      <p class="subtitle">Лёгкое приложение для проведения игровых сессий D&D</p>

      <div class="actions">
        <BasePanel variant="elevated" class="create-session-panel">
          <template #header>
            <h3>Создать сессию</h3>
          </template>
          <div class="panel-content">
            <p class="description">Создайте новую игровую сессию и станьте Game Master</p>
            <BaseButton
              variant="primary"
              size="lg"
              :disabled="loading"
              @click="handleCreateSession"
            >
              Создать сессию
            </BaseButton>
          </div>
        </BasePanel>

        <BasePanel variant="elevated" class="join-session-panel">
          <template #header>
            <h3>Присоединиться к сессии</h3>
          </template>
          <div class="panel-content">
            <p class="description">Введите код комнаты и ваше имя</p>
            <div class="form">
              <BaseInput
                v-model="joinCode"
                placeholder="Код комнаты (например: ABC123)"
                class="code-input"
              />
              <BaseInput
                v-model="playerName"
                placeholder="Ваше имя"
                class="name-input"
              />
              <BaseButton
                variant="primary"
                :disabled="!canJoin || loading"
                @click="handleJoinSession"
              >
                Присоединиться
              </BaseButton>
            </div>
          </div>
        </BasePanel>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'

const router = useRouter()
const sessionStore = useSessionStore()

const joinCode = ref('')
const playerName = ref('')
const loading = ref(false)

const canJoin = computed(() => {
  return joinCode.value.trim().length >= 6 && playerName.value.trim().length > 0
})

async function handleCreateSession() {
  loading.value = true
  try {
    await sessionStore.createSession()
    router.push({ name: 'gm-lobby' })
  } catch (error) {
    console.error('Failed to create session:', error)
    alert('Не удалось создать сессию. Попробуйте снова.')
  } finally {
    loading.value = false
  }
}

async function handleJoinSession() {
  if (!canJoin.value) return

  loading.value = true
  try {
    await sessionStore.joinSession(joinCode.value.toUpperCase().trim(), playerName.value.trim())
    router.push({ name: 'player-lobby' })
  } catch (error: any) {
    console.error('Failed to join session:', error)
    const message = error.response?.data?.detail || 'Не удалось присоединиться к сессии. Проверьте код комнаты.'
    alert(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--spacing-4);
  background: var(--color-bg-primary);
}

.container {
  width: 100%;
  max-width: 600px;
}

.title {
  text-align: center;
  font-size: var(--font-size-4xl);
  margin-bottom: var(--spacing-2);
  color: var(--color-text-primary);
}

.subtitle {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-8);
}

.actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.create-session-panel,
.join-session-panel {
  width: 100%;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.description {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.code-input,
.name-input {
  width: 100%;
}
</style>
