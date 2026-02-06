<template>
  <div class="edit-map-view">
    <div class="editor-header">
      <button class="back-btn" @click="router.push({ name: 'profile' })">
        <ArrowLeft :size="18" />
        <span>Назад</span>
      </button>
      <h1 class="map-name">{{ mapEditorStore.currentMap?.name || 'Загрузка...' }}</h1>
    </div>

    <div v-if="mapEditorStore.loading" class="loading-state">
      Загрузка карты...
    </div>

    <div v-else-if="!mapEditorStore.currentMap" class="error-state">
      Карта не найдена
    </div>

    <div v-else class="editor-canvas">
      <GameMap
        :editor-mode="true"
        :editor-map="mapEditorStore.activeMapForCanvas"
        @editor-add-token="handleAddToken"
        @editor-update-token="handleUpdateToken"
        @editor-delete-token="handleDeleteToken"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMapEditorStore } from '@/stores/mapEditor'
import { useToast } from '@/composables/useToast'
import { ArrowLeft } from 'lucide-vue-next'
import GameMap from '@/components/map/GameMap.vue'
import type { MapTokenCreate } from '@/types/models'

const route = useRoute()
const router = useRouter()
const mapEditorStore = useMapEditorStore()
const toast = useToast()

onMounted(async () => {
  const id = route.params.id as string
  try {
    await mapEditorStore.loadMap(id)
  } catch {
    toast.error('Не удалось загрузить карту')
  }
})

async function handleAddToken(data: MapTokenCreate) {
  try {
    await mapEditorStore.addToken({
      type: data.type,
      x: data.x,
      y: data.y,
      scale: data.scale,
      rotation: data.rotation,
      label: data.label,
      color: data.color ?? undefined,
      icon: data.icon ?? undefined,
      layer: data.layer,
    })
  } catch {
    toast.error('Не удалось добавить токен')
  }
}

async function handleUpdateToken(tokenId: string, data: { x: number; y: number }) {
  try {
    await mapEditorStore.updateToken(tokenId, data)
  } catch {
    toast.error('Не удалось обновить токен')
  }
}

async function handleDeleteToken(tokenId: string) {
  try {
    await mapEditorStore.deleteToken(tokenId)
  } catch {
    toast.error('Не удалось удалить токен')
  }
}
</script>

<style scoped>
.edit-map-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-bg-primary);
}

.editor-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all 150ms ease;
}

.back-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.map-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.editor-canvas {
  flex: 1;
  min-height: 0;
}

.loading-state,
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}
</style>
