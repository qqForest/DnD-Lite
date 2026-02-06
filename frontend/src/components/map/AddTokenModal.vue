<template>
  <BaseModal
    :model-value="modelValue"
    title="Добавить токен"
    size="md"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="add-token-modal">
      <!-- Mode Tabs -->
      <div class="mode-tabs">
        <button
          :class="['mode-tab', { active: mode === 'character' }]"
          @click="mode = 'character'"
        >
          <UserCircle :size="16" />
          Персонаж
        </button>
        <button
          :class="['mode-tab', { active: mode === 'custom' }]"
          @click="mode = 'custom'"
        >
          <Circle :size="16" />
          Произвольный
        </button>
      </div>

      <!-- Character Mode -->
      <div v-if="mode === 'character'" class="character-list">
        <div v-if="sessionCharacters.length === 0" class="empty-state">
          Нет персонажей в сессии
        </div>
        <div
          v-for="char in sessionCharacters"
          :key="char.id"
          :class="['character-item', {
            selected: selectedCharacterId === char.id,
            placed: placedCharacterIds.has(char.id)
          }]"
          @click="selectCharacter(char)"
        >
          <div class="character-color" :style="{ background: getCharacterColor(char) }"></div>
          <div class="character-info">
            <div class="character-name">{{ char.name }}</div>
            <div class="character-details">
              <span v-if="char.class_name">{{ char.class_name }} {{ char.level }}</span>
              <span class="character-player">{{ getPlayerName(char.player_id) }}</span>
            </div>
          </div>
          <span v-if="placedCharacterIds.has(char.id)" class="placed-badge">На карте</span>
          <Check v-else-if="selectedCharacterId === char.id" :size="18" class="check-icon" />
        </div>
      </div>

      <!-- Custom Mode -->
      <div v-if="mode === 'custom'" class="custom-form">
        <div class="form-group">
          <label>Название</label>
          <input
            v-model="customLabel"
            type="text"
            class="form-input"
            placeholder="Например: Гоблин, Сундук..."
          />
        </div>
        <div class="form-group">
          <label>Тип</label>
          <select v-model="customType" class="form-input">
            <option value="monster">Монстр</option>
            <option value="prop">Объект</option>
          </select>
        </div>
        <div class="form-group">
          <label>Цвет</label>
          <div class="color-palette">
            <button
              v-for="color in COLOR_PALETTE"
              :key="color"
              :class="['color-swatch', { selected: customColor === color }]"
              :style="{ background: color }"
              @click="customColor = color"
            ></button>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="modal-actions">
        <BaseButton variant="ghost" @click="close">Отмена</BaseButton>
        <BaseButton
          variant="primary"
          :disabled="!canAdd"
          @click="handleAdd"
        >
          Добавить
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { UserCircle, Circle, Check } from 'lucide-vue-next'
import type { Character, MapTokenCreate } from '@/types/models'
import { useCharactersStore } from '@/stores/characters'
import { useSessionStore } from '@/stores/session'
import { useMapStore } from '@/stores/map'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const PLAYER_COLORS = [
  '#4A90D9', '#D94A4A', '#4AD94A', '#D9D94A',
  '#9B59B6', '#E67E22', '#1ABC9C', '#E84393',
]

const COLOR_PALETTE = [
  '#D94A4A', '#E67E22', '#D9D94A', '#4AD94A',
  '#1ABC9C', '#4A90D9', '#9B59B6', '#E84393',
  '#8B4513', '#808080',
]

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'add': [data: MapTokenCreate]
}>()

const charactersStore = useCharactersStore()
const sessionStore = useSessionStore()
const mapStore = useMapStore()

const mode = ref<'character' | 'custom'>('character')
const selectedCharacterId = ref<number | null>(null)
const customLabel = ref('')
const customColor = ref(COLOR_PALETTE[0])
const customType = ref<'monster' | 'prop'>('monster')

const sessionCharacters = computed(() => {
  return charactersStore.characters.filter(c => {
    const player = sessionStore.players.find(p => p.id === c.player_id)
    return player && !player.is_gm
  })
})

const placedCharacterIds = computed(() => {
  const ids = new Set<number>()
  if (mapStore.activeMap) {
    for (const token of mapStore.activeMap.tokens) {
      if (token.character_id) {
        ids.add(token.character_id)
      }
    }
  }
  return ids
})

const canAdd = computed(() => {
  if (mode.value === 'character') {
    return selectedCharacterId.value !== null
  }
  return customLabel.value.trim().length > 0
})

function getPlayerName(playerId: number): string {
  const player = sessionStore.players.find(p => p.id === playerId)
  return player?.name || 'Неизвестный'
}

function getCharacterColor(char: Character): string {
  const nonGmPlayers = sessionStore.players.filter(p => !p.is_gm)
  const playerIndex = nonGmPlayers.findIndex(p => p.id === char.player_id)
  if (playerIndex === -1) return '#cccccc'
  return PLAYER_COLORS[playerIndex % PLAYER_COLORS.length]
}

function selectCharacter(char: Character) {
  if (placedCharacterIds.value.has(char.id)) return
  selectedCharacterId.value = char.id
}

function handleAdd() {
  if (!canAdd.value) return

  if (mode.value === 'character' && selectedCharacterId.value !== null) {
    const char = charactersStore.characters.find(c => c.id === selectedCharacterId.value)
    if (!char) return

    emit('add', {
      x: 0,
      y: 0,
      character_id: char.id,
      type: 'character',
      label: null,
      color: getCharacterColor(char),
    })
  } else {
    emit('add', {
      x: 0,
      y: 0,
      type: customType.value,
      label: customLabel.value.trim(),
      color: customColor.value,
    })
  }

  reset()
  close()
}

function reset() {
  mode.value = 'character'
  selectedCharacterId.value = null
  customLabel.value = ''
  customColor.value = COLOR_PALETTE[0]
  customType.value = 'monster'
}

function close() {
  reset()
  emit('update:modelValue', false)
}
</script>

<style scoped>
.add-token-modal {
  min-height: 300px;
}

.mode-tabs {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-4);
}

.mode-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  background: transparent;
  border: 1px solid var(--alpha-overlay-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.mode-tab:hover {
  background: var(--alpha-overlay-light);
}

.mode-tab.active {
  background: var(--alpha-overlay-medium);
  color: var(--color-accent-primary);
  border-color: var(--color-accent-primary);
}

.character-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  max-height: 350px;
  overflow-y: auto;
}

.character-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--radius-md);
  background: var(--color-bg-elevated);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.character-item:hover:not(.placed) {
  background: var(--alpha-overlay-light);
}

.character-item.selected {
  background: var(--alpha-overlay-medium);
  outline: 2px solid var(--color-accent-primary);
}

.character-item.placed {
  opacity: 0.5;
  cursor: not-allowed;
}

.character-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.character-info {
  flex: 1;
  min-width: 0;
}

.character-name {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.character-details {
  display: flex;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.character-player {
  color: var(--color-text-muted);
}

.placed-badge {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  padding: 2px 8px;
  background: var(--alpha-overlay-light);
  border-radius: var(--radius-sm);
}

.check-icon {
  color: var(--color-accent-primary);
}

.custom-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.form-input {
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--alpha-overlay-medium);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.color-palette {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.color-swatch {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.color-swatch:hover {
  transform: scale(1.1);
}

.color-swatch.selected {
  border-color: white;
  box-shadow: 0 0 0 2px var(--color-accent-primary);
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  padding: var(--spacing-8);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
}
</style>
