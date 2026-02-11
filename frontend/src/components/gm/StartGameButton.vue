<template>
  <div class="start-game-button-container">
    <BaseButton
      variant="primary"
      size="lg"
      :disabled="starting"
      @click="handleStartGame"
      class="start-button"
    >
      <Play :size="24" />
      <span>{{ starting ? 'Запуск игры...' : 'Войти в игру' }}</span>
    </BaseButton>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Play } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'

const router = useRouter()
const sessionStore = useSessionStore()
const toast = useToast()

const starting = ref(false)

async function handleStartGame() {
  if (!sessionStore.token) return

  starting.value = true
  try {
    await sessionStore.startSession()
    toast.success('Игра начата!')
    router.push({
      name: 'gm-with-code',
      params: { code: sessionStore.code }
    })
  } catch (error: any) {
    console.error('Failed to start session:', error)
    toast.error(error.response?.data?.detail || 'Не удалось начать игру')
  } finally {
    starting.value = false
  }
}
</script>

<style scoped>
.start-game-button-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--spacing-2);
}

.start-button {
  min-width: 180px;
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  box-shadow: var(--glow-accent);
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  text-align: center;
  margin: 0;
}
</style>
