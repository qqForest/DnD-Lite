<template>
  <div class="profile-view">
    <div class="container">
      <div class="profile-header">
        <div class="user-info">
          <span class="display-name">{{ authStore.user?.display_name }}</span>
          <span class="role-badge">{{ roleLabel }}</span>
        </div>
        <div class="header-actions">
          <BaseButton variant="ghost" size="sm" @click="router.push({ name: 'home' })">
            На главную
          </BaseButton>
          <BaseButton variant="ghost" size="sm" @click="handleLogout">
            Выйти
          </BaseButton>
        </div>
      </div>

      <!-- Player section -->
      <template v-if="isPlayer">
        <section class="section">
          <h2 class="section-title">Мои персонажи</h2>
          <div class="cards-grid">
            <UserCharacterCard
              v-for="char in profileStore.playerCharacters"
              :key="char.id"
              :character="char"
              :deletable="true"
              :editable="true"
              @delete="confirmDelete('character', char.id, char.name)"
              @edit="router.push({ name: 'edit-character', params: { id: char.id } })"
            />
            <AddCard label="Новый персонаж" @click="router.push({ name: 'create-character' })" />
          </div>
        </section>

        <section class="section">
          <h2 class="section-title">Присоединиться к игре</h2>
          <BaseButton variant="primary" @click="router.push({ name: 'join' })">
            Присоединиться
          </BaseButton>
        </section>
      </template>

      <!-- GM section -->
      <template v-if="isGm">
        <section class="section">
          <h2 class="section-title">Мои карты</h2>
          <div class="cards-grid">
            <UserMapCard
              v-for="map in profileStore.maps"
              :key="map.id"
              :map="map"
              :deletable="true"
              @delete="confirmDelete('map', map.id, map.name)"
            />
            <AddCard label="Новая карта" @click="router.push({ name: 'create-map' })" />
          </div>
        </section>

        <section class="section">
          <h2 class="section-title">NPC</h2>
          <div class="cards-grid">
            <UserCharacterCard
              v-for="npc in profileStore.npcCharacters"
              :key="npc.id"
              :character="npc"
              :deletable="true"
              :editable="true"
              @delete="confirmDelete('character', npc.id, npc.name)"
              @edit="router.push({ name: 'edit-character', params: { id: npc.id } })"
            />
            <AddCard label="Новый NPC" @click="router.push({ name: 'create-character', query: { npc: 'true' } })" />
          </div>
        </section>

        <section class="section">
          <h2 class="section-title">Создать сессию</h2>
          <BaseButton variant="primary" :disabled="creatingSession" @click="handleCreateSession">
            Создать сессию
          </BaseButton>
        </section>
      </template>
    </div>

    <ConfirmModal
      v-model="showDeleteModal"
      title="Подтверждение удаления"
      :message="`Удалить «${deleteTarget.name}»? Это действие нельзя отменить.`"
      confirm-text="Удалить"
      :danger="true"
      @confirm="executeDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import { useSessionStore } from '@/stores/session'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'
import AddCard from '@/components/profile/AddCard.vue'
import UserCharacterCard from '@/components/profile/UserCharacterCard.vue'
import UserMapCard from '@/components/profile/UserMapCard.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const profileStore = useProfileStore()
const sessionStore = useSessionStore()
const toast = useToast()

const creatingSession = ref(false)
const showDeleteModal = ref(false)
const deleteTarget = ref<{ type: 'character' | 'map'; id: number | string; name: string }>({ type: 'character', id: 0, name: '' })

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

function handleLogout() {
  authStore.logout()
  sessionStore.clearSession()
  router.push({ name: 'login' })
}

function confirmDelete(type: 'character' | 'map', id: number | string, name: string) {
  deleteTarget.value = { type, id, name }
  showDeleteModal.value = true
}

async function executeDelete() {
  showDeleteModal.value = false
  try {
    if (deleteTarget.value.type === 'character') {
      await profileStore.deleteCharacter(deleteTarget.value.id as number)
      toast.success('Удалено')
    } else {
      await profileStore.deleteMap(deleteTarget.value.id as string)
      toast.success('Удалено')
    }
  } catch (error) {
    console.error('Failed to delete:', error)
    toast.error('Не удалось удалить')
  }
}

async function handleCreateSession() {
  creatingSession.value = true
  try {
    await sessionStore.createSession()
    router.push({ name: 'gm-lobby' })
  } catch (error) {
    console.error('Failed to create session:', error)
    toast.error('Не удалось создать сессию')
  } finally {
    creatingSession.value = false
  }
}

onMounted(() => {
  profileStore.fetchCharacters()
  if (isGm.value) {
    profileStore.fetchMaps()
  }
})
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  padding: var(--spacing-6);
  background: var(--color-bg-primary);
}

.container {
  max-width: 960px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-8);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.display-name {
  font-size: var(--font-size-xl);
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

.header-actions {
  display: flex;
  gap: var(--spacing-2);
}

.section {
  margin-bottom: var(--spacing-8);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-4);
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
