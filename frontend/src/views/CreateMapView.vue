<template>
  <div class="create-map-view">
    <div class="container">
      <div class="header">
        <BaseButton variant="ghost" size="sm" @click="router.push({ name: 'profile' })">
          &larr; Назад
        </BaseButton>
      </div>

      <h1 class="title">Новая карта</h1>

      <section class="section">
        <div class="form-group">
          <label class="label">Название</label>
          <BaseInput v-model="form.name" placeholder="Название карты" />
          <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
        </div>

        <div class="dimensions">
          <div class="form-group">
            <label class="label">Ширина (px)</label>
            <input type="number" class="number-input" v-model.number="form.width" min="100" />
            <span v-if="errors.width" class="field-error">{{ errors.width }}</span>
          </div>
          <div class="form-group">
            <label class="label">Высота (px)</label>
            <input type="number" class="number-input" v-model.number="form.height" min="100" />
            <span v-if="errors.height" class="field-error">{{ errors.height }}</span>
          </div>
          <div class="form-group">
            <label class="label">Масштаб сетки</label>
            <input type="number" class="number-input" v-model.number="form.grid_scale" min="10" />
            <span v-if="errors.grid_scale" class="field-error">{{ errors.grid_scale }}</span>
          </div>
        </div>

        <div class="form-group">
          <label class="label">URL фона (опционально)</label>
          <BaseInput v-model="form.background_url" placeholder="https://example.com/map.jpg" />
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
import { useRouter } from 'vue-router'
import { userMapsApi } from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'

const router = useRouter()
const toast = useToast()
const submitting = ref(false)

const form = reactive({
  name: '',
  width: 1920,
  height: 1080,
  grid_scale: 50,
  background_url: '',
})

const errors = computed(() => {
  const e: Record<string, string> = {}
  if (form.name.length < 1 || form.name.length > 200) e.name = 'Название: 1-200 символов'
  if (form.width < 100) e.width = 'Минимум 100'
  if (form.height < 100) e.height = 'Минимум 100'
  if (form.grid_scale < 10) e.grid_scale = 'Минимум 10'
  return e
})

const canSubmit = computed(() => {
  return form.name.trim().length >= 1 && Object.keys(errors.value).length === 0
})

async function handleSubmit() {
  if (!canSubmit.value) return
  submitting.value = true
  try {
    await userMapsApi.create({
      name: form.name.trim(),
      width: form.width,
      height: form.height,
      grid_scale: form.grid_scale,
      background_url: form.background_url.trim() || null,
    })
    toast.success('Карта создана!')
    router.push({ name: 'profile' })
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось создать карту')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.create-map-view {
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

.dimensions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-3);
}

@media (max-width: 480px) {
  .dimensions {
    grid-template-columns: 1fr;
  }
}

.field-error {
  font-size: var(--font-size-xs);
  color: var(--color-danger, #ef4444);
  margin-top: 2px;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
}
</style>
