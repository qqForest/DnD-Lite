<template>
  <BasePanel variant="elevated" class="character-selection">
    <template #header>
      <h3 class="panel-title">Выберите персонажа</h3>
    </template>
    <div v-if="playerCharacters.length === 0" class="empty-state">
      <User :size="48" />
      <p>У вас пока нет персонажей</p>
      <BaseButton variant="primary" @click="showCreateModal = true">
        Создать персонажа
      </BaseButton>
    </div>
    <div v-else class="characters-list">
      <CharacterCard
        v-for="character in playerCharacters"
        :key="character.id"
        :character="character"
        :class="{ selected: charactersStore.selectedId === character.id }"
        @click="selectCharacter(character.id)"
      />
      <div class="create-button-wrapper">
        <BaseButton variant="secondary" @click="showCreateModal = true">
          + Создать еще
        </BaseButton>
      </div>
    </div>
    <CreateCharacterModal
      v-model="showCreateModal"
      @created="handleCharacterCreated"
    />
  </BasePanel>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { User } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import CharacterCard from '@/components/character/CharacterCard.vue'
import CreateCharacterModal from '@/components/gm/CreateCharacterModal.vue'

const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()

const showCreateModal = ref(false)

const playerCharacters = computed(() => {
  if (!sessionStore.currentPlayer) {
    const gmPlayer = sessionStore.players.find(p => p.is_gm)
    if (gmPlayer) {
      return charactersStore.characters.filter(c => c.player_id !== gmPlayer.id)
    }
    return charactersStore.characters
  }
  return charactersStore.byPlayer(sessionStore.currentPlayer.id)
})

function selectCharacter(characterId: number) {
  charactersStore.select(characterId)
}

function handleCharacterCreated(characterId: number) {
  charactersStore.select(characterId)
  showCreateModal.value = false
}
</script>

<style scoped>
.character-selection {
  width: 100%;
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
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-state svg {
  opacity: 0.5;
}

.characters-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  max-height: 400px;
  overflow-y: auto;
}

.characters-list :deep(.character-card) {
  transition: all var(--duration-fast);
  cursor: pointer;
}

.characters-list :deep(.character-card.selected) {
  border-left-width: 4px;
  background: var(--alpha-overlay-light);
  transform: translateX(2px);
}

.create-button-wrapper {
  padding-top: var(--spacing-2);
  display: flex;
  justify-content: center;
}
</style>
