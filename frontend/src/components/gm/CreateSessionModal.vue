<template>
  <BaseModal :model-value="modelValue" title="Создание сессии" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <div v-if="loading" class="loading">Загрузка карт...</div>
    <div v-else-if="maps.length === 0" class="empty">
      <p>У вас нет сохранённых карт в профиле.</p>
      <p class="hint">Вы можете добавить карту позже в лобби сессии.</p>
    </div>
    <div v-else>
      <p class="section-label">Выберите карту для сессии (необязательно):</p>
      <div class="maps-grid">
        <div
          v-for="map in maps"
          :key="map.id"
          class="map-select-card"
          :class="{ selected: selectedMapId === map.id }"
          @click="toggleMap(map.id)"
        >
          <UserMapCard :map="map" />
        </div>
      </div>
    </div>
    <template #footer>
      <div class="modal-actions">
        <BaseButton variant="ghost" @click="$emit('update:modelValue', false)">
          Отмена
        </BaseButton>
        <BaseButton
          v-if="maps.length > 0 && selectedMapId"
          variant="secondary"
          :disabled="creating"
          @click="handleCreate()"
        >
          Без карты
        </BaseButton>
        <BaseButton variant="primary" :disabled="creating" @click="handleCreate(selectedMapId || undefined)">
          {{ selectedMapId ? 'Создать с картой' : 'Создать сессию' }}
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
import UserMapCard from '@/components/profile/UserMapCard.vue'

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

function toggleMap(id: string) {
  selectedMapId.value = selectedMapId.value === id ? null : id
}

function handleCreate(userMapId?: string) {
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
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-3) 0;
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
