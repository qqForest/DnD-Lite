<template>
  <div class="map-card">
    <div class="card-header">
      <span class="name">{{ map.name }}</span>
      <button v-if="deletable" class="delete-btn" @click.stop="$emit('delete')" title="Удалить">
        &times;
      </button>
    </div>

    <div class="card-info">
      <span class="dimensions">{{ map.width }} x {{ map.height }}</span>
      <span class="grid">Сетка: {{ map.grid_scale }}px</span>
    </div>

    <div class="map-preview" @click.stop="$emit('upload-background')">
      <img v-if="map.background_url" :src="map.background_url" class="preview-thumb" alt="Фон карты" />
      <span v-else class="preview-icon">&#x1F5FA;</span>
      <span class="upload-hint">{{ map.background_url ? 'Сменить фон' : 'Загрузить фон' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UserMap } from '@/types/models'

defineProps<{
  map: UserMap
  deletable?: boolean
}>()

defineEmits<{
  delete: []
  'upload-background': []
}>()
</script>

<style scoped>
.map-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  min-height: 160px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.name {
  font-weight: 600;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.delete-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.delete-btn:hover {
  color: var(--color-danger, #ef4444);
}

.card-info {
  display: flex;
  gap: var(--spacing-3);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.map-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  background: var(--color-bg-primary);
  border-radius: var(--radius-sm);
  min-height: 60px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.map-preview:hover .upload-hint {
  opacity: 1;
}

.preview-icon {
  font-size: 2rem;
  opacity: 0.4;
}

.preview-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  inset: 0;
}

.upload-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: var(--font-size-xs);
  text-align: center;
  padding: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}
</style>
