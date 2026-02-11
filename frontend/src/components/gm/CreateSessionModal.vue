<template>
  <BaseModal :model-value="modelValue" title="Создание сессии" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <div v-if="loading" class="loading">Загрузка карт...</div>
    <div v-else-if="maps.length === 0" class="empty">
      <p>У вас нет сохранённых карт в профиле.</p>
      <p class="hint">Создайте карту в профиле, чтобы начать сессию.</p>
    </div>
    <div v-else>
      <p class="section-label">Выберите карту для сессии:</p>
      <div class="maps-grid">
        <div
          v-for="map in maps"
          :key="map.id"
          class="map-select-card"
          :class="{ selected: selectedMapId === map.id }"
          @click="selectMap(map.id)"
        >
          <div class="map-preview">
            <img v-if="map.background_url" :src="map.background_url" alt="" class="preview-img" />
            <div v-else class="preview-placeholder">
              <span class="preview-icon">🗺️</span>
            </div>
          </div>
          <div class="map-info">
            <span class="map-name">{{ map.name }}</span>
            <span class="map-meta">{{ map.width }} × {{ map.height }}</span>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <div class="modal-actions">
        <BaseButton variant="ghost" size="lg" @click="$emit('update:modelValue', false)">
          Отмена
        </BaseButton>
        <BaseButton
          variant="primary"
          size="lg"
          :disabled="creating || !selectedMapId"
          @click="handleCreate(selectedMapId!)"
        >
          Создать сессию
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useProfileStore } from '@/stores/profile'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  create: [userMapId?: string]
}>()

const profileStore = useProfileStore()

const selectedMapId = ref<string | null>(null)
const creating = ref(false)
const loading = ref(false)

const maps = computed(() => profileStore.maps)

watch(() => props.modelValue, async (open) => {
  if (open) {
    selectedMapId.value = null
    loading.value = true
    await profileStore.fetchMaps()
    loading.value = false
  }
})

function selectMap(id: string) {
  selectedMapId.value = id
}

function handleCreate(userMapId: string) {
  creating.value = true
  emit('create', userMapId)
}
</script>

<style scoped>
.loading,
.empty {
  text-align: center;
  padding: var(--spacing-6);
  color: var(--color-text-secondary);
}

.empty p {
  margin: 0;
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-top: var(--spacing-2) !important;
}

.section-label {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-4) 0;
}

.maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--spacing-3);
  max-height: 420px;
  overflow-y: auto;
  padding: 2px;
}

.map-select-card {
  cursor: pointer;
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-border);
  background: var(--color-bg-secondary);
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.map-select-card:hover {
  border-color: var(--color-accent-primary, #c0a46c);
  transform: translateY(-2px);
}

.map-select-card.selected {
  border-color: var(--color-accent-primary, #c0a46c);
  box-shadow: 0 0 0 2px var(--color-accent-primary, #c0a46c);
}

.map-preview {
  aspect-ratio: 16 / 9;
  background: var(--color-bg-primary);
  overflow: hidden;
  position: relative;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-icon {
  font-size: 2rem;
  opacity: 0.3;
}

.map-info {
  padding: var(--spacing-2) var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.map-name {
  font-family: var(--font-family-display);
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
}
</style>
