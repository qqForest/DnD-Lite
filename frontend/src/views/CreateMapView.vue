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
          <label class="label">Фон карты (опционально)</label>
          <div
            class="upload-zone"
            :class="{ 'drag-over': isDragOver, 'has-preview': !!previewUrl }"
            @dragover.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @drop.prevent="handleDrop"
            @click="fileInput?.click()"
          >
            <template v-if="previewUrl">
              <img :src="previewUrl" class="preview-img" alt="Превью фона" />
              <button class="remove-bg-btn" @click.stop="removeBackground" title="Удалить фон">&times;</button>
            </template>
            <template v-else>
              <span v-if="uploading" class="upload-text">Загрузка...</span>
              <span v-else class="upload-text">Перетащите JPG/PNG или нажмите для выбора</span>
            </template>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png"
            style="display: none"
            @change="handleFileSelect"
          />
          <span v-if="uploadError" class="field-error">{{ uploadError }}</span>
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

const fileInput = ref<HTMLInputElement | null>(null)
const isDragOver = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const previewUrl = ref('')

const form = reactive({
  name: '',
  width: 1920,
  height: 1080,
  grid_scale: 50,
  background_url: '',
})

async function uploadFile(file: File) {
  const allowed = ['image/jpeg', 'image/png']
  if (!allowed.includes(file.type)) {
    uploadError.value = 'Только JPG/PNG файлы'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = 'Файл слишком большой (макс. 10МБ)'
    return
  }
  uploadError.value = ''
  uploading.value = true
  try {
    const result = await userMapsApi.uploadBackground(file)
    form.background_url = result.url
    form.width = result.width
    form.height = result.height
    previewUrl.value = result.url
  } catch (err: any) {
    uploadError.value = err.response?.data?.detail || 'Ошибка загрузки'
  } finally {
    uploading.value = false
  }
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) {
    uploadFile(input.files[0])
    input.value = ''
  }
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) uploadFile(file)
}

function removeBackground() {
  form.background_url = ''
  previewUrl.value = ''
  form.width = 1920
  form.height = 1080
}

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
  min-height: 100dvh;
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

.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-6);
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-zone:hover {
  border-color: var(--color-primary);
}

.upload-zone.drag-over {
  border-color: var(--color-primary);
  background: rgba(99, 102, 241, 0.08);
}

.upload-zone.has-preview {
  padding: var(--spacing-2);
}

.upload-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.preview-img {
  max-width: 100%;
  max-height: 200px;
  border-radius: var(--radius-sm);
  object-fit: contain;
}

.remove-bg-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.remove-bg-btn:hover {
  background: var(--color-danger, #ef4444);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
}
</style>
