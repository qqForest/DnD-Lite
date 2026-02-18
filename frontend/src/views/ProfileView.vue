<template>
  <div class="profile-view">
    <ProfileTopBar @toggle-sidebar="showSidebar = !showSidebar" />
    <ProfileSidebar v-model="showSidebar" />

    <div class="container">
      <!-- Player section -->
      <template v-if="isPlayer">
        <section class="section">
          <h2 class="section-title">Мои персонажи</h2>
          <CharacterCarousel
            :characters="profileStore.playerCharacters"
            @delete="(id) => confirmDelete('character', id, getCharName(id))"
            @edit="(id) => router.push({ name: 'edit-character', params: { id } })"
          />
          <div class="section-action">
            <BaseButton
              variant="primary"
              class="full-width-btn"
              @click="router.push({ name: 'create-character' })"
            >
              Новый персонаж
            </BaseButton>
          </div>
        </section>

        <section class="section">
          <h2 class="section-title">Присоединиться к игре</h2>
          <div class="section-action">
            <BaseButton
              variant="primary"
              class="full-width-btn"
              @click="router.push({ name: 'join' })"
            >
              Присоединиться
            </BaseButton>
          </div>
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
              @edit="router.push({ name: 'edit-map', params: { id: map.id } })"
              @upload-background="startBgUpload(map.id)"
            />
            <AddCard label="Новая карта" @click="router.push({ name: 'create-map' })" />
          </div>
        </section>

        <section class="section">
          <h2 class="section-title">NPC</h2>
          <div class="npc-grid">
            <CharacterFlipCard
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
          <div class="section-action">
            <BaseButton
              variant="primary"
              size="lg"
              class="full-width-btn"
              :disabled="creatingSession"
              @click="showCreateModal = true"
            >
              Создать сессию
            </BaseButton>
          </div>
        </section>
      </template>
    </div>

    <input
      ref="bgFileInput"
      type="file"
      accept="image/jpeg,image/png"
      style="display: none"
      @change="handleBgFileChange"
    />

    <ConfirmModal
      v-model="showDeleteModal"
      title="Подтверждение удаления"
      :message="`Удалить «${deleteTarget.name}»? Это действие нельзя отменить.`"
      confirm-text="Удалить"
      :danger="true"
      @confirm="executeDelete"
    />

    <CreateSessionModal
      v-model="showCreateModal"
      @create="handleCreateSession"
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
import { userMapsApi } from '@/services/api'
import BaseButton from '@/components/common/BaseButton.vue'
import AddCard from '@/components/profile/AddCard.vue'
import CharacterFlipCard from '@/components/profile/CharacterFlipCard.vue'
import UserMapCard from '@/components/profile/UserMapCard.vue'
import CharacterCarousel from '@/components/profile/CharacterCarousel.vue'
import ProfileTopBar from '@/components/profile/ProfileTopBar.vue'
import ProfileSidebar from '@/components/profile/ProfileSidebar.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import CreateSessionModal from '@/components/gm/CreateSessionModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const profileStore = useProfileStore()
const sessionStore = useSessionStore()
const toast = useToast()

const showSidebar = ref(false)
const creatingSession = ref(false)
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const deleteTarget = ref<{ type: 'character' | 'map'; id: number | string; name: string }>({ type: 'character', id: 0, name: '' })

const bgFileInput = ref<HTMLInputElement | null>(null)
const bgUploadMapId = ref<string | null>(null)

const role = computed(() => authStore.user?.role || 'player')
const isPlayer = computed(() => role.value === 'player' || role.value === 'both')
const isGm = computed(() => role.value === 'gm' || role.value === 'both')

function getCharName(id: number): string {
  const char = profileStore.playerCharacters.find(c => c.id === id)
  return char?.name || ''
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

function startBgUpload(mapId: string) {
  bgUploadMapId.value = mapId
  bgFileInput.value?.click()
}

async function handleBgFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || !bgUploadMapId.value) return

  try {
    const result = await userMapsApi.uploadBackground(file)
    await userMapsApi.update(bgUploadMapId.value, {
      background_url: result.url,
      width: result.width,
      height: result.height,
    })
    await profileStore.fetchMaps()
    toast.success('Фон загружен')
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось загрузить фон')
  }
}

async function handleCreateSession(userMapId?: string) {
  creatingSession.value = true
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
  min-height: 100dvh;
  background: var(--color-bg-primary);
}

.container {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--spacing-6);
}

.section {
  margin-bottom: var(--spacing-8);
}

.section-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-4);
}

.section-action {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-4);
}

.full-width-btn {
  width: 100%;
  max-width: 300px;
  min-height: 48px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-4);
}

.npc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

@media (min-width: 1200px) {
  .npc-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .npc-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .npc-grid {
    grid-template-columns: 1fr;
  }
}
</style>
