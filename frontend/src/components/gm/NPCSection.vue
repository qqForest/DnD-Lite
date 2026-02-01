<template>
  <BasePanel variant="elevated" class="npc-section">
    <template #header>
      <div class="header-content">
        <h3 class="panel-title">NPC (Неигровые персонажи)</h3>
        <BaseButton variant="primary" size="sm" @click="showCreateModal = true">
          <Plus :size="16" />
          Создать NPC
        </BaseButton>
      </div>
    </template>
    <div v-if="npcs.length === 0" class="empty-state">
      <User :size="48" />
      <p>Нет созданных NPC</p>
      <p class="hint">Создайте неигровых персонажей для вашей сессии</p>
    </div>
    <div v-else class="npcs-grid">
      <div
        v-for="npc in npcs"
        :key="npc.id"
        class="npc-card-wrapper"
      >
        <CharacterCard :character="npc" />
        <button class="delete-button" @click="handleDelete(npc.id)" title="Удалить NPC">
          <Trash2 :size="16" />
        </button>
      </div>
    </div>

    <CreateCharacterModal
      v-model="showCreateModal"
      @created="handleCharacterCreated"
    />
  </BasePanel>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Plus, User, Trash2 } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useToast } from '@/composables/useToast'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import CharacterCard from '@/components/character/CharacterCard.vue'
import CreateCharacterModal from './CreateCharacterModal.vue'

const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const toast = useToast()

const showCreateModal = ref(false)

const npcs = computed(() => {
  const gmPlayer = sessionStore.players.find(p => p.is_gm)
  if (!gmPlayer) return []
  return charactersStore.byPlayer(gmPlayer.id)
})

function handleCharacterCreated(characterId: number) {
  charactersStore.fetchAll()
  toast.success('NPC создан!')
}

async function handleDelete(characterId: number) {
  if (!confirm('Вы уверены, что хотите удалить этого NPC?')) return
  
  try {
    await charactersStore.remove(characterId)
    toast.success('NPC удален')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Не удалось удалить NPC')
  }
}
</script>

<style scoped>
.npc-section {
  width: 100%;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-title {
  margin: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-8);
  color: var(--color-text-secondary);
  text-align: center;
}

.empty-state svg {
  opacity: 0.5;
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.npcs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-4);
  max-height: 500px;
  overflow-y: auto;
}

.npc-card-wrapper {
  position: relative;
}

.delete-button {
  position: absolute;
  top: var(--spacing-2);
  right: var(--spacing-2);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--color-danger);
  color: var(--color-text-primary);
  border-radius: var(--radius-md);
  opacity: 0;
  transition: all var(--duration-fast);
  z-index: 10;
}

.npc-card-wrapper:hover .delete-button {
  opacity: 1;
}

.delete-button:hover {
  filter: brightness(1.1);
}
</style>
