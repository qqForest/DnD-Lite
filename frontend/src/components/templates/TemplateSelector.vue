<template>
  <div class="template-selector">
    <div v-if="loading" class="loading">
      Загрузка шаблонов...
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="templates-grid">
      <ClassTemplateCard
        v-for="template in filteredTemplates"
        :key="template.id"
        :template="template"
        :is-selected="selectedTemplateId === template.id"
        @select="selectTemplate(template.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { ClassTemplateListItem } from '@/types/models'
import { templatesApi } from '@/services/api'
import ClassTemplateCard from './ClassTemplateCard.vue'

const props = defineProps<{
  searchQuery?: string
}>()

const emit = defineEmits<{
  'template-selected': [templateId: string]
}>()

const templates = ref<ClassTemplateListItem[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const selectedTemplateId = ref<string | null>(null)

const filteredTemplates = computed(() => {
  if (!props.searchQuery) return templates.value
  const query = props.searchQuery.toLowerCase()
  return templates.value.filter(t =>
    t.name_ru.toLowerCase().includes(query) ||
    t.name.toLowerCase().includes(query) ||
    t.description_ru.toLowerCase().includes(query)
  )
})

async function loadTemplates() {
  loading.value = true
  error.value = null
  try {
    templates.value = await templatesApi.list()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Не удалось загрузить шаблоны классов'
    console.error('Failed to load templates:', err)
  } finally {
    loading.value = false
  }
}

function selectTemplate(templateId: string) {
  selectedTemplateId.value = templateId
  emit('template-selected', templateId)
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-selector {
  width: 100%;
}

.loading,
.error {
  text-align: center;
  padding: var(--spacing-8);
  color: var(--color-text-secondary);
}

.error {
  color: var(--color-danger);
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-4);
  max-height: 400px;
  overflow-y: auto;
  padding: var(--spacing-2);
}

@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
}
</style>
