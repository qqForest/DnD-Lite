<template>
  <div class="join-view">
    <!-- Экран подключения -->
    <div v-if="loading" class="connecting-screen">
      <div class="spinner"></div>
      <p class="connecting-text">Подключение...</p>
    </div>

    <!-- Основной контент -->
    <div v-else class="container">
      <div class="header">
        <BaseButton variant="ghost" size="sm" @click="router.push({ name: 'profile' })">
          &larr; Назад
        </BaseButton>
        <h1 class="title">Присоединиться</h1>
      </div>

      <!-- Карусель персонажей -->
      <section v-if="profileStore.playerCharacters.length > 0" class="section">
        <CharacterCarousel
          ref="carouselRef"
          :characters="profileStore.playerCharacters"
          :readonly="true"
        />
        <p class="carousel-hint">Выбрать персонажа</p>
      </section>

      <!-- Пустое состояние -->
      <section v-else class="section empty-state">
        <p class="empty-text">У вас нет персонажей</p>
        <BaseButton variant="primary" @click="router.push({ name: 'create-character' })">
          Создать персонажа
        </BaseButton>
      </section>

      <!-- Код сессии -->
      <section class="section code-section">
        <input
          v-model="sessionCode"
          class="code-input"
          placeholder="Код комнаты"
          maxlength="6"
          autocomplete="off"
          spellcheck="false"
        />
      </section>

      <!-- Кнопка присоединиться -->
      <section class="section action-section">
        <BaseButton
          variant="primary"
          :disabled="!canJoin"
          class="join-btn"
          @click="handleJoin"
        >
          Присоединиться
        </BaseButton>

        <p v-if="error" class="error-message">{{ error }}</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/common/BaseButton.vue'
import CharacterCarousel from '@/components/profile/CharacterCarousel.vue'

const router = useRouter()
const route = useRoute()
const profileStore = useProfileStore()
const sessionStore = useSessionStore()
const authStore = useAuthStore()

const carouselRef = ref<InstanceType<typeof CharacterCarousel> | null>(null)
const sessionCode = ref('')
const loading = ref(false)
const error = ref('')

const selectedCharacterId = computed(() => {
  const idx = carouselRef.value?.currentIndex ?? 0
  return profileStore.playerCharacters[idx]?.id ?? null
})

const canJoin = computed(() => {
  return sessionCode.value.trim().length >= 6 && selectedCharacterId.value !== null && !loading.value
})

async function handleJoin() {
  if (!canJoin.value) return

  loading.value = true
  error.value = ''
  try {
    const playerName = authStore.user?.display_name || ''
    await sessionStore.joinSession(
      sessionCode.value.toUpperCase().trim(),
      playerName,
      selectedCharacterId.value!
    )
    router.push({
      name: 'player-lobby-with-code',
      params: { code: sessionStore.code }
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Не удалось присоединиться к сессии. Проверьте код комнаты.'
    loading.value = false
  }
}

onMounted(() => {
  profileStore.fetchCharacters()

  // Pre-fill code from URL if present
  const codeFromUrl = route.params.code as string | undefined
  if (codeFromUrl) {
    sessionCode.value = codeFromUrl.toUpperCase()
  }
})
</script>

<style scoped>
.join-view {
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--spacing-6);
  background: var(--color-bg-primary);
  display: flex;
  justify-content: center;
}

.container {
  width: 100%;
  max-width: 700px;
}

.header {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
}

.title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.section {
  margin-bottom: var(--spacing-6);
}

.carousel-hint {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-2);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-8) 0;
}

.empty-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.code-section {
  display: flex;
  justify-content: center;
}

.code-input {
  width: 100%;
  max-width: 300px;
  min-height: 48px;
  padding: var(--spacing-3);
  font-family: monospace;
  font-size: var(--font-size-xl);
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  outline: none;
  transition: border-color var(--duration-fast);
}

.code-input::placeholder {
  text-transform: none;
  letter-spacing: normal;
  font-family: inherit;
  font-size: var(--font-size-base);
  color: var(--color-text-muted, var(--color-text-secondary));
}

.code-input:focus {
  border-color: var(--color-accent-primary);
  box-shadow: var(--glow-accent);
}

.action-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
}

.join-btn {
  width: 100%;
  max-width: 300px;
  min-height: 48px;
}

.error-message {
  color: var(--color-danger, #ef4444);
  font-size: var(--font-size-sm);
}

/* Экран подключения */
.connecting-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  gap: var(--spacing-4);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.connecting-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}
</style>
