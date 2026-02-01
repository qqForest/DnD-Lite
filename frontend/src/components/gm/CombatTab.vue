<template>
  <div class="combat-tab">
    <div v-if="!combatStore.isActive" class="combat-start">
      <button
        class="start-combat-btn"
        @click="handleStartCombat"
        :disabled="isStarting"
      >
        <Swords :size="20" />
        <span>Начать бой</span>
      </button>
      <p class="hint">Начните бой, чтобы игроки могли бросить инициативу</p>
    </div>

    <div v-else class="combat-active">
      <div class="combat-header">
        <h3>Бой активен</h3>
        <button
          class="end-combat-btn"
          @click="handleEndCombat"
          :disabled="isEnding"
        >
          <X :size="16" />
          Завершить
        </button>
      </div>

      <div class="initiative-section">
        <h4>Порядок инициативы</h4>
        <InitiativeList />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Swords, X } from 'lucide-vue-next'
import { useCombatStore } from '@/stores/combat'
import { useSessionStore } from '@/stores/session'
import InitiativeList from '@/components/combat/InitiativeList.vue'

const combatStore = useCombatStore()
const sessionStore = useSessionStore()

const isStarting = ref(false)
const isEnding = ref(false)

async function handleStartCombat() {
  if (!sessionStore.token || isStarting.value) return
  
  isStarting.value = true
  try {
    await combatStore.startCombat()
  } catch (error) {
    console.error('Failed to start combat:', error)
  } finally {
    isStarting.value = false
  }
}

async function handleEndCombat() {
  if (!sessionStore.token || isEnding.value) return
  
  isEnding.value = true
  try {
    await combatStore.endCombat()
  } catch (error) {
    console.error('Failed to end combat:', error)
  } finally {
    isEnding.value = false
  }
}
</script>

<style scoped>
.combat-tab {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.combat-start {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-6) 0;
}

.start-combat-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-5);
  background: var(--color-danger);
  color: var(--color-text-on-primary);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  transition: all var(--duration-fast);
  box-shadow: var(--shadow-md);
}

.start-combat-btn:hover:not(:disabled) {
  background: var(--color-danger-hover, #dc2626);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.start-combat-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  text-align: center;
  margin: 0;
}

.combat-active {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.combat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--alpha-overlay-light);
}

.combat-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.end-combat-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2) var(--spacing-3);
  background: transparent;
  color: var(--color-danger);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--duration-fast);
}

.end-combat-btn:hover:not(:disabled) {
  background: var(--color-danger);
  color: var(--color-text-on-primary);
}

.end-combat-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.initiative-section h4 {
  margin: 0 0 var(--spacing-3) 0;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}
</style>
