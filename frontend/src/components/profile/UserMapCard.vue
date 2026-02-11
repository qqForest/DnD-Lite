<template>
  <div class="map-card">
    <div class="map-preview" @click.stop="$emit('upload-background')">
      <img v-if="map.background_url" :src="map.background_url" class="preview-thumb" alt="Фон карты" />
      <div v-else class="preview-placeholder">
        <span class="preview-icon">&#x1F5FA;</span>
      </div>
      <div class="upload-hint">{{ map.background_url ? 'Сменить фон' : 'Загрузить фон' }}</div>
    </div>

    <div class="card-body">
      <div class="card-header">
        <span class="name">{{ map.name }}</span>
        <div class="card-actions">
          <button class="action-btn edit-btn" @click.stop="$emit('edit')" title="Редактировать">
            &#x270E;
          </button>
          <button v-if="deletable" class="action-btn delete-btn" @click.stop="$emit('delete')" title="Удалить">
            &times;
          </button>
        </div>
      </div>

      <div class="card-info">
        <span class="dimensions">{{ map.width }} x {{ map.height }}</span>
        <span class="separator">·</span>
        <span class="grid">{{ map.grid_scale }}px</span>
      </div>
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
  edit: []
  'upload-background': []
}>()
</script>

<style scoped>
.map-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.map-card:hover {
  border-color: var(--color-accent-primary, #c0a46c);
}

.map-preview {
  aspect-ratio: 3 / 4;
  width: 100%;
  background: var(--color-bg-primary);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.map-preview:hover .upload-hint {
  opacity: 1;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-icon {
  font-size: 3rem;
  opacity: 0.3;
}

.preview-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-size: var(--font-size-xs);
  text-align: center;
  padding: var(--spacing-2);
  opacity: 0;
  transition: opacity 0.2s;
  backdrop-filter: blur(4px);
}

.card-body {
  padding: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-2);
}

.name {
  font-family: var(--font-family-display);
  font-weight: 600;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.action-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  transition: color 150ms ease;
}

.edit-btn:hover {
  color: var(--color-accent-primary, #c0a46c);
}

.delete-btn:hover {
  color: var(--color-danger, #ef4444);
}

.card-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.separator {
  opacity: 0.5;
}
</style>
