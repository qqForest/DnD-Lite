<template>
  <BaseModal
    :model-value="modelValue"
    title="Добавить токен"
    size="md"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="add-token-modal">
      <!-- Mode Tabs -->
      <div v-if="!hideCharacterTab" class="mode-tabs">
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
      <div v-if="mode === 'character' && !hideCharacterTab" class="character-list">
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
      <div v-if="mode === 'custom'" class="custom-mode">
        <!-- Sub-mode tabs -->
        <div class="sub-mode-tabs">
          <button
            :class="['sub-mode-tab', { active: customSubMode === 'templates' }]"
            @click="customSubMode = 'templates'"
          >
            Шаблоны
          </button>
          <button
            :class="['sub-mode-tab', { active: customSubMode === 'manual' }]"
            @click="customSubMode = 'manual'"
          >
            Ручной
          </button>
        </div>

        <!-- Templates Grid -->
        <div v-if="customSubMode === 'templates'" class="templates-grid">
          <div
            v-for="template in TOKEN_TEMPLATES"
            :key="template.iconKey"
            :class="['template-item', { selected: selectedTemplateKey === template.iconKey }]"
            @click="selectTemplate(template)"
          >
            <div class="template-preview" :style="{ background: template.color }">
              <svg viewBox="0 0 512 512" width="28" height="28">
                <path :d="getIconPath(template.iconKey)" fill="white" />
              </svg>
            </div>
            <span class="template-name">{{ template.label }}</span>
          </div>
        </div>

        <!-- Manual Mode -->
        <div v-if="customSubMode === 'manual'" class="custom-form">
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
          <div class="form-group">
            <label>Иконка <span class="optional-label">(необязательно)</span></label>
            <div class="icon-picker">
              <button
                :class="['icon-pick-item', { selected: selectedIconKey === null }]"
                @click="selectedIconKey = null"
              >
                <div class="icon-pick-none">—</div>
              </button>
              <button
                v-for="icon in TOKEN_ICONS"
                :key="icon.key"
                :class="['icon-pick-item', { selected: selectedIconKey === icon.key }]"
                :title="icon.name_ru"
                @click="selectedIconKey = icon.key"
              >
                <svg viewBox="0 0 512 512" width="24" height="24">
                  <path :d="icon.pathData" fill="currentColor" />
                </svg>
              </button>
            </div>
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
import { TOKEN_ICONS, TOKEN_TEMPLATES, getTokenIcon } from '@/data/tokenIcons'
import type { TokenTemplate } from '@/data/tokenIcons'

const PLAYER_COLORS = [
  '#4A90D9', '#D94A4A', '#4AD94A', '#D9D94A',
  '#9B59B6', '#E67E22', '#1ABC9C', '#E84393',
]

const COLOR_PALETTE = [
  '#D94A4A', '#E67E22', '#D9D94A', '#4AD94A',
  '#1ABC9C', '#4A90D9', '#9B59B6', '#E84393',
  '#8B4513', '#808080',
]

const props = defineProps<{
  modelValue: boolean
  hideCharacterTab?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'add': [data: MapTokenCreate]
}>()

const charactersStore = useCharactersStore()
const sessionStore = useSessionStore()
const mapStore = useMapStore()

const mode = ref<'character' | 'custom'>(props.hideCharacterTab ? 'custom' : 'character')
const customSubMode = ref<'templates' | 'manual'>('templates')
const selectedCharacterId = ref<number | null>(null)
const selectedTemplateKey = ref<string | null>(null)
const customLabel = ref('')
const customColor = ref(COLOR_PALETTE[0])
const customType = ref<'monster' | 'prop'>('monster')
const selectedIconKey = ref<string | null>(null)

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
  if (customSubMode.value === 'templates') {
    return selectedTemplateKey.value !== null
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

function getIconPath(iconKey: string): string {
  return getTokenIcon(iconKey)?.pathData ?? ''
}

function selectCharacter(char: Character) {
  if (placedCharacterIds.value.has(char.id)) return
  selectedCharacterId.value = char.id
}

function selectTemplate(template: TokenTemplate) {
  selectedTemplateKey.value = template.iconKey
  // Заполняем ручные поля на случай переключения в ручной режим
  customLabel.value = template.label
  customColor.value = template.color
  customType.value = template.type
  selectedIconKey.value = template.iconKey
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
  } else if (customSubMode.value === 'templates' && selectedTemplateKey.value) {
    const template = TOKEN_TEMPLATES.find(t => t.iconKey === selectedTemplateKey.value)
    if (!template) return

    emit('add', {
      x: 0,
      y: 0,
      type: template.type,
      label: customLabel.value.trim() || template.label,
      color: template.color,
      icon: template.iconKey,
    })
  } else {
    emit('add', {
      x: 0,
      y: 0,
      type: customType.value,
      label: customLabel.value.trim(),
      color: customColor.value,
      icon: selectedIconKey.value,
    })
  }

  reset()
  close()
}

function reset() {
  mode.value = props.hideCharacterTab ? 'custom' : 'character'
  customSubMode.value = 'templates'
  selectedCharacterId.value = null
  selectedTemplateKey.value = null
  customLabel.value = ''
  customColor.value = COLOR_PALETTE[0]
  customType.value = 'monster'
  selectedIconKey.value = null
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

/* Sub-mode tabs */
.sub-mode-tabs {
  display: flex;
  gap: var(--spacing-1);
  margin-bottom: var(--spacing-3);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  padding: 2px;
}

.sub-mode-tab {
  flex: 1;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.sub-mode-tab:hover {
  color: var(--color-text-primary);
}

.sub-mode-tab.active {
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* Templates Grid */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-2);
  max-height: 320px;
  overflow-y: auto;
}

.template-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2);
  border-radius: var(--radius-md);
  background: var(--color-bg-elevated);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.template-item:hover {
  background: var(--alpha-overlay-light);
}

.template-item.selected {
  border-color: var(--color-accent-primary);
  background: var(--alpha-overlay-medium);
}

.template-preview {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.template-name {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
  line-height: 1.2;
}

/* Custom Form */
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

.optional-label {
  font-weight: normal;
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
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

/* Icon Picker */
.icon-picker {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-1);
}

.icon-pick-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: var(--color-bg-tertiary);
  border: 2px solid transparent;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
}

.icon-pick-item:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.icon-pick-item.selected {
  border-color: var(--color-accent-primary);
  background: var(--alpha-overlay-medium);
  color: var(--color-accent-primary);
}

.icon-pick-none {
  font-size: var(--font-size-lg);
  color: var(--color-text-muted);
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
