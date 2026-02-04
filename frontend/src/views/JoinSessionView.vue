<template>
  <div class="join-view">
    <div class="container">
      <div class="header">
        <BaseButton variant="ghost" size="sm" @click="router.push({ name: 'profile' })">
          &larr; Назад
        </BaseButton>
      </div>

      <h1 class="title">Присоединиться к игре</h1>

      <section class="section" v-if="profileStore.playerCharacters.length > 0">
        <h2 class="section-title">Выберите персонажа</h2>
        <div class="characters-grid">
          <UserCharacterCard
            v-for="char in profileStore.playerCharacters"
            :key="char.id"
            :character="char"
            :selected="selectedCharacterId === char.id"
            :clickable="true"
            @select="selectedCharacterId = char.id"
          />
        </div>
      </section>

      <section class="section" v-else>
        <p class="no-characters">
          У вас пока нет персонажей.
          <router-link :to="{ name: 'create-character' }" class="create-link">Создать персонажа</router-link>
        </p>
      </section>

      <section class="section">
        <h2 class="section-title">Данные для входа</h2>
        <div class="form">
          <BaseInput
            v-model="sessionCode"
            placeholder="Код комнаты (например: ABC123)"
          />
          <BaseInput
            v-model="playerName"
            placeholder="Ваше имя"
          />
          <p v-if="profileStore.playerCharacters.length > 0 && !selectedCharacterId" class="warning-message">
            Вы войдёте без персонажа
          </p>
          <BaseButton
            variant="primary"
            size="lg"
            :disabled="!canJoin || loading"
            @click="handleJoin"
          >
            Присоединиться
          </BaseButton>
        </div>
      </section>

      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profile'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import UserCharacterCard from '@/components/profile/UserCharacterCard.vue'

const router = useRouter()
const profileStore = useProfileStore()
const sessionStore = useSessionStore()
const authStore = useAuthStore()

const selectedCharacterId = ref<number | null>(null)
const sessionCode = ref('')
const playerName = ref(authStore.user?.display_name || '')
const loading = ref(false)
const error = ref('')

const canJoin = computed(() => {
  return sessionCode.value.trim().length >= 6 && playerName.value.trim().length > 0
})

async function handleJoin() {
  if (!canJoin.value) return

  loading.value = true
  error.value = ''
  try {
    await sessionStore.joinSession(
      sessionCode.value.toUpperCase().trim(),
      playerName.value.trim(),
      selectedCharacterId.value ?? undefined
    )
    router.push({ name: 'player-lobby' })
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Не удалось присоединиться к сессии. Проверьте код комнаты.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  profileStore.fetchCharacters()
})
</script>

<style scoped>
.join-view {
  min-height: 100vh;
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
  margin-bottom: var(--spacing-4);
}

.title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-6);
}

.section {
  margin-bottom: var(--spacing-6);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-3);
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
}

@media (max-width: 480px) {
  .characters-grid {
    grid-template-columns: 1fr;
  }
}

.no-characters {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.create-link {
  color: var(--color-primary);
  text-decoration: underline;
}

.warning-message {
  color: var(--color-warning, #f59e0b);
  font-size: var(--font-size-sm);
}

.error-message {
  color: var(--color-danger, #ef4444);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-2);
}
</style>
