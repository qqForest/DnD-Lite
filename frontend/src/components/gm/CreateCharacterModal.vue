<template>
  <BaseModal
    :model-value="modelValue"
    title="Создать персонажа"
    size="lg"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="create-character-modal">
      <!-- Шаг 1: Выбор шаблона -->
      <div v-if="step === 1" class="step step-1">
        <h3 class="step-title">Выберите класс</h3>
        <TemplateSelector
          :search-query="searchQuery"
          @template-selected="handleTemplateSelected"
        />
      </div>

      <!-- Шаг 2: Форма создания -->
      <div v-if="step === 2" class="step step-2">
        <div v-if="selectedTemplate" class="template-preview">
          <h3 class="step-title">Создание персонажа: {{ selectedTemplate.name_ru }}</h3>
          <div class="template-info">
            <p class="template-description">{{ selectedTemplate.description_ru }}</p>
            <div class="template-stats">
              <div class="stat-item">
                <span class="stat-label">Hit Die:</span>
                <span class="stat-value">{{ selectedTemplate.hit_die }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Рекомендуемое HP:</span>
                <span class="stat-value">{{ selectedTemplate.recommended_hp }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="form">
          <div class="form-group">
            <label for="character-name">Имя персонажа *</label>
            <BaseInput
              id="character-name"
              v-model="formData.name"
              placeholder="Введите имя персонажа"
            />
          </div>

          <div class="form-group">
            <label for="character-level">Уровень</label>
            <input
              id="character-level"
              v-model.number="formData.level"
              type="number"
              min="1"
              max="20"
              class="level-input"
            />
          </div>

          <div class="form-options">
            <label class="checkbox-label">
              <input
                v-model="formData.include_items"
                type="checkbox"
                class="checkbox"
              />
              <span>Включить стартовые предметы</span>
            </label>

            <label class="checkbox-label">
              <input
                v-model="formData.include_spells"
                type="checkbox"
                class="checkbox"
              />
              <span>Включить стартовые заклинания</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="modal-footer">
        <BaseButton
          v-if="step === 2"
          variant="secondary"
          @click="step = 1"
        >
          Назад
        </BaseButton>
        <BaseButton
          variant="ghost"
          @click="close"
        >
          Отмена
        </BaseButton>
        <BaseButton
          v-if="step === 2"
          variant="primary"
          :disabled="!canCreate || creating"
          @click="handleCreate"
        >
          {{ creating ? 'Создание...' : 'Создать' }}
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ClassTemplateResponse } from '@/types/models'
import { templatesApi } from '@/services/api'
import { useCharactersStore } from '@/stores/characters'
import { useToast } from '@/composables/useToast'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import TemplateSelector from '@/components/templates/TemplateSelector.vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'created': [characterId: number]
}>()

const charactersStore = useCharactersStore()
const toast = useToast()

const step = ref<1 | 2>(1)
const searchQuery = ref('')
const selectedTemplateId = ref<string | null>(null)
const selectedTemplate = ref<ClassTemplateResponse | null>(null)
const creating = ref(false)

const formData = ref({
  name: '',
  level: 1,
  include_items: true,
  include_spells: true
})

const canCreate = computed(() => {
  return formData.value.name.trim().length > 0 &&
    formData.value.level >= 1 &&
    formData.value.level <= 20 &&
    selectedTemplateId.value !== null
})

async function handleTemplateSelected(templateId: string) {
  selectedTemplateId.value = templateId
  try {
    selectedTemplate.value = await templatesApi.get(templateId)
    step.value = 2
  } catch (error) {
    console.error('Failed to load template details:', error)
  }
}

async function handleCreate() {
  if (!canCreate.value || !selectedTemplateId.value) return

  creating.value = true
  try {
    const character = await charactersStore.createFromTemplate({
      template_id: selectedTemplateId.value,
      name: formData.value.name.trim(),
      level: formData.value.level,
      include_items: formData.value.include_items,
      include_spells: formData.value.include_spells
    })
    toast.success(`Персонаж "${character.name}" успешно создан!`)
    emit('created', character.id)
    reset()
    close()
  } catch (error: any) {
    console.error('Failed to create character:', error)
    const message = error.response?.data?.detail || 'Не удалось создать персонажа'
    toast.error(message)
  } finally {
    creating.value = false
  }
}

function reset() {
  step.value = 1
  searchQuery.value = ''
  selectedTemplateId.value = null
  selectedTemplate.value = null
  formData.value = {
    name: '',
    level: 1,
    include_items: true,
    include_spells: true
  }
}

function close() {
  reset()
  emit('update:modelValue', false)
}
</script>

<style scoped>
.create-character-modal {
  min-height: 400px;
}

.step {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.step-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-4) 0;
}

.template-preview {
  padding: var(--spacing-4);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-4);
}

.template-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.template-description {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.template-stats {
  display: flex;
  gap: var(--spacing-4);
}

.stat-item {
  display: flex;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
}

.stat-label {
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

.stat-value {
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-semibold);
}

.form {
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

.level-input {
  width: 100px;
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--alpha-overlay-medium);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: var(--font-family-mono);
}

.level-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.form-options {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
}
</style>
