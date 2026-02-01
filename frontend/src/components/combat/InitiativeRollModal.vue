<template>
  <Transition name="modal">
    <div
      v-if="showModal"
      class="initiative-modal-overlay"
      @click.self
    >
      <div class="initiative-modal-card">
        <div class="modal-header">
          <h2>Бросок инициативы</h2>
        </div>

        <div class="modal-main">
          <!-- Before rolling -->
          <template v-if="!hasRolled && !isRolling">
            <div 
              class="dice-button"
              @click="handleRoll"
              role="button"
              tabindex="0"
            >
              <span class="dice-icon">🎲</span>
              <span class="dice-label">Нажмите для броска</span>
            </div>
          </template>

          <!-- Rolling animation -->
          <template v-else-if="isRolling">
            <div class="dice-rolling">
              <span class="dice-icon spinning">🎲</span>
              <span class="rolling-label">Бросаем...</span>
            </div>
          </template>

          <!-- Result -->
          <template v-else>
            <div class="result-display">
              <div class="result-value">{{ rollResult }}</div>
              <div class="result-label">Ваша инициатива</div>
            </div>
          </template>
        </div>

        <div v-if="hasRolled" class="modal-footer">
          <p class="auto-close-hint">Окно закроется автоматически...</p>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCombatStore } from '@/stores/combat'
import { useSessionStore } from '@/stores/session'

const combatStore = useCombatStore()
const sessionStore = useSessionStore()

const localRollResult = ref<number | null>(null)
const isRolling = ref(false)

const showModal = computed(() => combatStore.showInitiativeModal)
const hasRolled = computed(() => localRollResult.value !== null)
const rollResult = computed(() => localRollResult.value)

async function handleRoll() {
  if (isRolling.value || hasRolled.value) return
  
  isRolling.value = true
  
  try {
    if (sessionStore.token) {
      const result = await combatStore.rollInitiative(sessionStore.token)
      localRollResult.value = result
      
      // Auto-close after 2 seconds
      setTimeout(() => {
        combatStore.closeInitiativeModal()
        localRollResult.value = null
      }, 2000)
    }
  } catch (error) {
    console.error('Failed to roll initiative:', error)
  } finally {
    isRolling.value = false
  }
}

// Reset state when modal closes
watch(showModal, (newVal) => {
  if (!newVal) {
    localRollResult.value = null
    isRolling.value = false
  }
})
</script>

<style scoped>
.initiative-modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--alpha-overlay-heavy);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  backdrop-filter: blur(4px);
  animation: fadeIn var(--duration-fast) var(--ease-out);
}

.initiative-modal-card {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-xl);
  min-width: 320px;
  max-width: 90vw;
  animation: slideIn var(--duration-normal) var(--ease-bounce);
  text-align: center;
}

.modal-header h2 {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.modal-main {
  padding: var(--spacing-8) 0;
}

.dice-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-6);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast);
  background: var(--alpha-overlay-light);
}

.dice-button:hover {
  background: var(--color-primary);
  transform: scale(1.05);
}

.dice-button:active {
  transform: scale(0.98);
}

.dice-icon {
  font-size: 80px;
  line-height: 1;
}

.dice-label {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.dice-button:hover .dice-label {
  color: var(--color-text-on-primary);
}

.dice-rolling {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
}

.dice-icon.spinning {
  animation: spin 0.5s linear infinite;
}

.rolling-label {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.result-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
}

.result-value {
  font-family: var(--font-family-display);
  font-size: 72px;
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  line-height: 1;
  animation: popIn var(--duration-normal) var(--ease-bounce);
}

.result-label {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.modal-footer {
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--alpha-overlay-light);
}

.auto-close-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  0% {
    transform: scale(0.5) translateY(20px);
    opacity: 0;
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes popIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Transition animations */
.modal-enter-active {
  animation: fadeIn var(--duration-fast) var(--ease-out);
}

.modal-leave-active {
  transition: opacity var(--duration-normal) var(--ease-out);
}

.modal-leave-to {
  opacity: 0;
}
</style>
