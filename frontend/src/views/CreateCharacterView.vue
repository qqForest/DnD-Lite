<template>
  <div class="create-character-view">
    <div class="container">
      <div class="header">
        <BaseButton variant="ghost" size="sm" @click="router.push({ name: 'profile' })">
          &larr; Назад
        </BaseButton>
      </div>

      <h1 class="title">{{ isNpc ? 'Новый NPC' : 'Новый персонаж' }}</h1>

      <!-- Template selector -->
      <section class="section" v-if="!isNpc">
        <h2 class="section-title">Шаблон класса (опционально)</h2>
        <TemplateSelector @template-selected="handleTemplateSelected" />
      </section>

      <section class="section">
        <h2 class="section-title">Основные данные</h2>
        <div class="form-group">
          <label class="label">Имя</label>
          <BaseInput v-model="form.name" placeholder="Имя персонажа" />
          <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
        </div>

        <div class="form-group">
          <label class="label">Класс</label>
          <BaseInput v-model="form.class_name" placeholder="Класс (например: Воин)" />
        </div>

        <div class="form-group">
          <label class="label">Уровень</label>
          <input
            type="number"
            class="number-input"
            v-model.number="form.level"
            min="1"
            max="20"
          />
          <span v-if="errors.level" class="field-error">{{ errors.level }}</span>
        </div>
      </section>

      <section class="section">
        <h2 class="section-title">Характеристики</h2>
        <div class="stats-grid">
          <div class="stat-field" v-for="stat in statFields" :key="stat.key">
            <label class="label">{{ stat.label }}</label>
            <input
              type="number"
              class="number-input"
              v-model.number="(form as any)[stat.key]"
              min="1"
              max="30"
            />
            <span v-if="(errors as any)[stat.key]" class="field-error">{{ (errors as any)[stat.key] }}</span>
          </div>
        </div>
      </section>

      <section class="section">
        <h2 class="section-title">Внешность</h2>
        <div class="form-group">
          <label class="label">Описание внешности (для генерации аватара)</label>
          <textarea
            class="appearance-textarea"
            v-model="form.appearance"
            placeholder="Опишите внешность персонажа: раса, телосложение, черты лица, одежда, особые приметы..."
            rows="3"
          ></textarea>
        </div>
      </section>

      <section class="section">
        <h2 class="section-title">Здоровье</h2>
        <div class="hp-fields">
          <div class="form-group">
            <label class="label">Макс. HP</label>
            <input
              type="number"
              class="number-input"
              v-model.number="form.max_hp"
              min="1"
            />
            <span v-if="errors.max_hp" class="field-error">{{ errors.max_hp }}</span>
          </div>
          <div class="form-group">
            <label class="label">Текущие HP</label>
            <input
              type="number"
              class="number-input"
              v-model.number="form.current_hp"
              min="0"
              :max="form.max_hp"
            />
            <span v-if="errors.current_hp" class="field-error">{{ errors.current_hp }}</span>
          </div>
        </div>
      </section>

      <div class="form-actions">
        <BaseButton variant="ghost" @click="router.push({ name: 'profile' })">
          Отмена
        </BaseButton>
        <BaseButton variant="primary" :disabled="!canSubmit || submitting" @click="handleSubmit">
          Создать
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { userCharactersApi, templatesApi } from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import TemplateSelector from '@/components/templates/TemplateSelector.vue'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const isNpc = computed(() => route.query.npc === 'true')
const submitting = ref(false)

const form = reactive({
  name: '',
  class_name: '',
  level: 1,
  strength: 10,
  dexterity: 10,
  constitution: 10,
  intelligence: 10,
  wisdom: 10,
  charisma: 10,
  max_hp: 10,
  current_hp: 10,
  appearance: '',
})

const statFields = [
  { key: 'strength', label: 'Сила' },
  { key: 'dexterity', label: 'Ловкость' },
  { key: 'constitution', label: 'Телосложение' },
  { key: 'intelligence', label: 'Интеллект' },
  { key: 'wisdom', label: 'Мудрость' },
  { key: 'charisma', label: 'Харизма' },
]

const errors = computed(() => {
  const e: Record<string, string> = {}
  if (form.name.length < 1 || form.name.length > 100) e.name = 'Имя: 1-100 символов'
  if (form.level < 1 || form.level > 20) e.level = 'Уровень: 1-20'
  for (const stat of statFields) {
    const val = (form as any)[stat.key]
    if (val < 1 || val > 30) e[stat.key] = '1-30'
  }
  if (form.max_hp < 1) e.max_hp = 'Минимум 1'
  if (form.current_hp < 0 || form.current_hp > form.max_hp) e.current_hp = `0-${form.max_hp}`
  return e
})

const canSubmit = computed(() => {
  return form.name.trim().length >= 1 && Object.keys(errors.value).length === 0
})

async function handleTemplateSelected(templateId: string) {
  try {
    const template = await templatesApi.get(templateId)
    form.class_name = template.name_ru
    form.strength = template.strength
    form.dexterity = template.dexterity
    form.constitution = template.constitution
    form.intelligence = template.intelligence
    form.wisdom = template.wisdom
    form.charisma = template.charisma
    form.max_hp = template.recommended_hp
    form.current_hp = template.recommended_hp
  } catch (err) {
    console.error('Failed to load template:', err)
  }
}

async function handleSubmit() {
  if (!canSubmit.value) return
  submitting.value = true
  try {
    await userCharactersApi.create({
      name: form.name.trim(),
      class_name: form.class_name.trim() || null,
      level: form.level,
      is_npc: isNpc.value,
      strength: form.strength,
      dexterity: form.dexterity,
      constitution: form.constitution,
      intelligence: form.intelligence,
      wisdom: form.wisdom,
      charisma: form.charisma,
      max_hp: form.max_hp,
      current_hp: form.current_hp,
      appearance: form.appearance.trim() || null,
    })
    toast.success(isNpc.value ? 'NPC создан!' : 'Персонаж создан!')
    router.push({ name: 'profile' })
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось создать персонажа')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.create-character-view {
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

.form-group {
  margin-bottom: var(--spacing-3);
}

.label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-1);
}

.number-input {
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.number-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-3);
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.hp-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3);
}

.field-error {
  font-size: var(--font-size-xs);
  color: var(--color-danger, #ef4444);
  margin-top: 2px;
  display: block;
}

.appearance-textarea {
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: inherit;
  resize: vertical;
}

.appearance-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
}
</style>
