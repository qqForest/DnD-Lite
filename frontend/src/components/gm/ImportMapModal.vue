<template>
  <BaseModal :model-value="modelValue" title="Загрузить карту из профиля" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="maps.length === 0" class="empty">
      У вас нет сохраненных карт в профиле.
    </div>
    <div v-else class="maps-grid">
      <div
        v-for="map in maps"
        :key="map.id"
        class="map-select-card"
        :class="{ selected: selectedId === map.id }"
        @click="selectedId = map.id"
      >
        <UserMapCard :map="map" />
      </div>
    </div>
    <template #footer>
      <div class="modal-actions">
        <BaseButton variant="ghost" @click="$emit('update:modelValue', false)">
          Отмена
        </BaseButton>
        <BaseButton variant="primary" :disabled="!selectedId || importing" @click="handleImport">
          Загрузить
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useProfileStore } from '@/stores/profile'
import { useToast } from '@/composables/useToast'
import { mapsApi } from '@/services/api'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import UserMapCard from '@/components/profile/UserMapCard.vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  imported: []
}>()

const profileStore = useProfileStore()
const toast = useToast()

const selectedId = ref<string | null>(null)
const importing = ref(false)
const loading = ref(false)

const maps = computed(() => profileStore.maps)

watch(() => props.modelValue, async (open) => {
  if (open) {
    selectedId.value = null
    loading.value = true
    await profileStore.fetchMaps()
    loading.value = false
  }
})

async function handleImport() {
  if (!selectedId.value) return
  const map = maps.value.find(m => m.id === selectedId.value)
  if (!map) return

  importing.value = true
  try {
    await mapsApi.create({
      name: map.name,
      background_url: map.background_url,
      width: map.width,
      height: map.height,
      grid_scale: map.grid_scale,
    })
    toast.success('Карта загружена в сессию!')
    emit('imported')
    emit('update:modelValue', false)
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось загрузить карту')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.loading,
.empty {
  text-align: center;
  padding: var(--spacing-6);
  color: var(--color-text-secondary);
}

.maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-3);
  max-height: 400px;
  overflow-y: auto;
}

.map-select-card {
  cursor: pointer;
  border-radius: var(--radius-lg);
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.map-select-card:hover {
  border-color: var(--color-primary);
}

.map-select-card.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
}
</style>
