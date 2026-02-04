<template>
  <BaseModal :model-value="modelValue" title="Импорт NPC из профиля" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="npcCharacters.length === 0" class="empty">
      У вас нет сохраненных NPC в профиле.
    </div>
    <div v-else class="npc-grid">
      <UserCharacterCard
        v-for="npc in npcCharacters"
        :key="npc.id"
        :character="npc"
        :clickable="true"
        :selected="selectedId === npc.id"
        @select="selectedId = npc.id"
      />
    </div>
    <template #footer>
      <div class="modal-actions">
        <BaseButton variant="ghost" @click="$emit('update:modelValue', false)">
          Отмена
        </BaseButton>
        <BaseButton variant="primary" :disabled="!selectedId || importing" @click="handleImport">
          Импортировать
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useProfileStore } from '@/stores/profile'
import { useCharactersStore } from '@/stores/characters'
import { useToast } from '@/composables/useToast'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import UserCharacterCard from '@/components/profile/UserCharacterCard.vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  imported: []
}>()

const profileStore = useProfileStore()
const charactersStore = useCharactersStore()
const toast = useToast()

const selectedId = ref<number | null>(null)
const importing = ref(false)
const loading = ref(false)

const npcCharacters = computed(() => profileStore.npcCharacters)

watch(() => props.modelValue, async (open) => {
  if (open) {
    selectedId.value = null
    loading.value = true
    await profileStore.fetchCharacters()
    loading.value = false
  }
})

async function handleImport() {
  if (!selectedId.value) return
  const npc = npcCharacters.value.find(c => c.id === selectedId.value)
  if (!npc) return

  importing.value = true
  try {
    await charactersStore.create({
      name: npc.name,
      class_name: npc.class_name,
      level: npc.level,
      strength: npc.strength,
      dexterity: npc.dexterity,
      constitution: npc.constitution,
      intelligence: npc.intelligence,
      wisdom: npc.wisdom,
      charisma: npc.charisma,
      max_hp: npc.max_hp,
      current_hp: npc.current_hp,
    })
    toast.success('NPC импортирован в сессию!')
    emit('imported')
    emit('update:modelValue', false)
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось импортировать NPC')
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

.npc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-3);
  max-height: 400px;
  overflow-y: auto;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
}
</style>
