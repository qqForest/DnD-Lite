<template>
  <BaseModal
    :model-value="modelValue"
    title="Начать бой"
    size="md"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="combat-setup">
      <h3 class="setup-title">Выберите NPC для участия в бою:</h3>

      <div v-if="availableNPCs.length === 0" class="empty-state">
        Нет NPC в сессии. Создайте NPC в лобби перед началом боя.
      </div>

      <div v-else class="npcs-list">
        <label
          v-for="npc in availableNPCs"
          :key="npc.id"
          class="npc-item"
        >
          <input
            type="checkbox"
            :value="npc.id"
            v-model="selectedNPCs"
            class="npc-checkbox"
          />
          <div class="npc-info">
            <span class="npc-name">{{ npc.name }}</span>
            <span class="npc-details">
              {{ npc.class_name || 'NPC' }} {{ npc.level }}
              <span class="npc-hp">{{ npc.current_hp }}/{{ npc.max_hp }} HP</span>
            </span>
          </div>
        </label>
      </div>
    </div>

    <template #footer>
      <div class="modal-actions">
        <BaseButton variant="ghost" @click="handleCancel">
          Отмена
        </BaseButton>
        <BaseButton
          variant="primary"
          :disabled="isStarting"
          @click="handleStart"
        >
          {{ isStarting ? 'Начинаем...' : 'Начать бой' }}
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCharactersStore } from '@/stores/characters'
import { useSessionStore } from '@/stores/session'
import { useCombatStore } from '@/stores/combat'
import { useToast } from '@/composables/useToast'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const charactersStore = useCharactersStore()
const sessionStore = useSessionStore()
const combatStore = useCombatStore()
const toast = useToast()

const selectedNPCs = ref<number[]>([])
const isStarting = ref(false)

const availableNPCs = computed(() => {
  const gmPlayer = sessionStore.players.find(p => p.is_gm)
  if (!gmPlayer) return []

  return charactersStore.characters.filter(c => c.player_id === gmPlayer.id)
})

async function handleStart() {
  if (isStarting.value) return

  isStarting.value = true
  try {
    console.log('[CombatSetup] Starting combat...')
    // Start combat
    await combatStore.startCombat()
    console.log('[CombatSetup] Combat started, rolling initiative for NPCs:', selectedNPCs.value)

    // Roll initiative for each selected NPC
    for (const npcId of selectedNPCs.value) {
      try {
        console.log(`[CombatSetup] Rolling initiative for NPC ${npcId}...`)
        const roll = await combatStore.rollInitiativeForNpc(npcId)
        console.log(`[CombatSetup] NPC ${npcId} rolled: ${roll}`)
      } catch (error) {
        console.error(`[CombatSetup] Failed to roll initiative for NPC ${npcId}:`, error)
        toast.error(`Не удалось бросить инициативу за NPC ${npcId}`)
      }
    }

    // Close modal and reset selection
    selectedNPCs.value = []
    emit('update:modelValue', false)
  } catch (error) {
    console.error('[CombatSetup] Failed to start combat:', error)
    toast.error('Не удалось начать бой')
  } finally {
    isStarting.value = false
  }
}

function handleCancel() {
  selectedNPCs.value = []
  emit('update:modelValue', false)
}
</script>

<style scoped>
.combat-setup {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.setup-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0;
}

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  padding: var(--spacing-8);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

.npcs-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  max-height: 350px;
  overflow-y: auto;
}

.npc-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--radius-md);
  background: var(--color-bg-elevated);
  cursor: pointer;
  transition: all var(--duration-fast);
  border: 2px solid transparent;
}

.npc-item:hover {
  background: var(--alpha-overlay-light);
}

.npc-item:has(.npc-checkbox:checked) {
  background: var(--alpha-overlay-medium);
  border-color: var(--color-accent-primary);
}

.npc-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-accent-primary);
  flex-shrink: 0;
}

.npc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  min-width: 0;
}

.npc-name {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.npc-details {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.npc-hp {
  padding: 2px 6px;
  background: var(--alpha-overlay-medium);
  border-radius: var(--radius-sm);
  font-weight: var(--font-weight-medium);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-2);
}
</style>
