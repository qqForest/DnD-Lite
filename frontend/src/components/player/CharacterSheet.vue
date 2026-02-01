<template>
  <div class="character-sheet">
    <div v-if="playerCharacters.length === 0" class="empty-state">
      <p class="empty-message">У вас пока нет персонажей</p>
      <p class="empty-hint">GM создаст персонажа для вас</p>
    </div>
    
    <div v-else class="characters-list">
      <CharacterCard
        v-for="character in playerCharacters"
        :key="character.id"
        :character="character"
        :class="{ selected: selectedCharacterId === character.id }"
        @click="selectCharacter(character.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCharactersStore } from '@/stores/characters'
import { useSessionStore } from '@/stores/session'
import CharacterCard from '@/components/character/CharacterCard.vue'

const charactersStore = useCharactersStore()
const sessionStore = useSessionStore()

const selectedCharacterId = computed(() => charactersStore.selectedId)

const playerCharacters = computed(() => {
  // Для игрока показываем всех персонажей, которые не принадлежат GM
  // В будущем можно улучшить, чтобы находить персонажей конкретного игрока по токену
  if (!sessionStore.currentPlayer) {
    // Если currentPlayer не определен, показываем всех персонажей кроме GM
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
</script>

<style scoped>
.character-sheet {
  padding: var(--spacing-4);
  max-height: 40vh;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-8);
  color: var(--color-text-secondary);
}

.empty-message {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  margin: 0 0 var(--spacing-2) 0;
}

.empty-hint {
  font-size: var(--font-size-sm);
  margin: 0;
  color: var(--color-text-muted);
}

.characters-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.characters-list :deep(.character-card) {
  transition: all var(--duration-fast);
}

.characters-list :deep(.character-card.selected) {
  border-left-width: 4px;
  background: var(--alpha-overlay-light);
  transform: translateX(2px);
}

@media (min-width: 1024px) {
  .character-sheet {
    max-height: none;
    height: 100%;
    overflow-y: auto;
  }
}
</style>
