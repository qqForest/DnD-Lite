<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-backdrop" @click="close">
        <div class="dice-modal" @click.stop>
          <div class="modal-header">
            <h3>Бросок кубика</h3>
            <button class="close-btn" @click="close">×</button>
          </div>

          <div class="modal-body">
            <div class="dice-grid">
              <button
                v-for="dice in diceTypes"
                :key="dice"
                :class="['dice-option', { selected: selectedDice === dice }]"
                @click="selectedDice = dice"
              >
                <span class="dice-icon">🎲</span>
                <span class="dice-label">{{ dice }}</span>
              </button>
            </div>

            <div class="modifier-section">
              <label for="modifier">Модификатор:</label>
              <input
                id="modifier"
                v-model.number="modifier"
                type="number"
                class="modifier-input"
                placeholder="0"
              />
            </div>

            <div class="custom-section">
              <label for="custom">Или своя формула:</label>
              <input
                id="custom"
                v-model="customFormula"
                type="text"
                class="custom-input"
                placeholder="2d6+3"
                @keyup.enter="handleRoll"
              />
            </div>
          </div>

          <div class="modal-footer">
            <BaseButton variant="secondary" @click="close">
              Отмена
            </BaseButton>
            <BaseButton
              variant="primary"
              :disabled="!canRoll || rolling"
              @click="handleRoll"
            >
              {{ rolling ? 'Бросаем...' : 'Бросить!' }}
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import BaseButton from '@/components/common/BaseButton.vue'
import { useDiceStore } from '@/stores/dice'
import { useToast } from '@/composables/useToast'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const diceStore = useDiceStore()
const toast = useToast()

const diceTypes = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100']
const selectedDice = ref<string>('d20')
const modifier = ref<number>(0)
const customFormula = ref('')
const rolling = ref(false)

const canRoll = computed(() => {
  return selectedDice.value || customFormula.value.trim().length > 0
})

// Reset when modal opens
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    selectedDice.value = 'd20'
    modifier.value = 0
    customFormula.value = ''
  }
})

function close() {
  emit('update:modelValue', false)
}

async function handleRoll() {
  if (!canRoll.value || rolling.value) return

  rolling.value = true
  try {
    let formula: string

    if (customFormula.value.trim()) {
      formula = customFormula.value.trim()
    } else {
      const mod = modifier.value || 0
      formula = mod !== 0
        ? `${selectedDice.value}${mod > 0 ? '+' : ''}${mod}`
        : selectedDice.value
    }

    await diceStore.roll(formula)
    close()
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Ошибка броска')
  } finally {
    rolling.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--alpha-overlay-heavy);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  backdrop-filter: blur(4px);
}

.dice-modal {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: min(600px, 90vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) var(--spacing-6);
  border-bottom: 1px solid var(--alpha-overlay-light);
}

.modal-header h3 {
  margin: 0;
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
}

.close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: var(--font-size-3xl);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
}

.close-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--spacing-6);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.dice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: var(--spacing-3);
}

.dice-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-4) var(--spacing-2);
  background: var(--color-bg-elevated);
  border: 2px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.dice-option:hover {
  background: var(--alpha-overlay-medium);
  transform: translateY(-2px);
}

.dice-option.selected {
  border-color: var(--color-accent-primary);
  background: var(--color-bg-elevated);
  box-shadow: 0 0 20px rgba(233, 69, 96, 0.4);
}

.dice-icon {
  font-size: 48px;
  filter: grayscale(100%);
  transition: filter var(--duration-fast);
}

.dice-option.selected .dice-icon,
.dice-option:hover .dice-icon {
  filter: grayscale(0%);
}

.dice-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  font-family: var(--font-family-mono);
  color: var(--color-text-primary);
}

.modifier-section,
.custom-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.modifier-section label,
.custom-section label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.modifier-input,
.custom-input {
  width: 100%;
  padding: var(--spacing-3);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--alpha-overlay-medium);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: var(--font-family-mono);
  transition: all var(--duration-fast);
}

.modifier-input:focus,
.custom-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.2);
}

.modifier-input::placeholder,
.custom-input::placeholder {
  color: var(--color-text-muted);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  padding: var(--spacing-4) var(--spacing-6);
  border-top: 1px solid var(--alpha-overlay-light);
  background: var(--alpha-overlay-light);
}

/* Animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--duration-normal) var(--ease-default);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .dice-modal,
.modal-leave-active .dice-modal {
  transition: transform var(--duration-normal) var(--ease-default);
}

.modal-enter-from .dice-modal,
.modal-leave-to .dice-modal {
  transform: scale(0.9) translateY(20px);
}
</style>
