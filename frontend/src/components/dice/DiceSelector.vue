<template>
  <div class="dice-selector">
    <div class="dice-buttons">
      <DiceButton
        v-for="dice in diceTypes"
        :key="dice"
        :type="dice"
        :is-active="selectedDice === dice"
        @select="selectedDice = dice"
      />
    </div>

    <div class="roll-controls">
      <BaseInput
        v-model="modifier"
        type="number"
        placeholder="+0"
        class="modifier-input"
      />
      <BaseButton
        variant="primary"
        :disabled="!selectedDice || rolling"
        @click="handleRoll"
      >
        {{ rolling ? 'Бросок...' : 'Бросить' }}
      </BaseButton>
    </div>

    <div v-if="customRollVisible" class="custom-roll">
      <BaseInput
        v-model="customFormula"
        placeholder="2d6+3"
        @keyup.enter="handleCustomRoll"
      />
      <BaseButton
        variant="secondary"
        size="sm"
        :disabled="rolling"
        @click="handleCustomRoll"
      >
        Бросить
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DiceButton from './DiceButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import { useDiceStore } from '@/stores/dice'
import { useToast } from '@/composables/useToast'

const diceStore = useDiceStore()
const toast = useToast()

const diceTypes = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100']
const selectedDice = ref<string>('d20')
const modifier = ref<number>(0)
const customFormula = ref('')
const customRollVisible = ref(false)
const rolling = ref(false)

async function handleRoll() {
  if (!selectedDice.value || rolling.value) return

  rolling.value = true
  try {
    const mod = modifier.value || 0
    const formula = mod !== 0 ? `${selectedDice.value}${mod > 0 ? '+' : ''}${mod}` : selectedDice.value
    await diceStore.roll(formula)
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Ошибка броска')
  } finally {
    rolling.value = false
  }
}

async function handleCustomRoll() {
  if (!customFormula.value || rolling.value) return

  rolling.value = true
  try {
    await diceStore.roll(customFormula.value)
    customFormula.value = ''
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Неверная формула')
  } finally {
    rolling.value = false
  }
}
</script>

<style scoped>
.dice-selector {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.dice-buttons {
  display: flex;
  gap: var(--spacing-2);
  overflow-x: auto;
  padding: var(--spacing-2) 0;
}

.roll-controls {
  display: flex;
  gap: var(--spacing-2);
  align-items: center;
}

.modifier-input {
  width: 80px;
}

.custom-roll {
  display: flex;
  gap: var(--spacing-2);
  padding-top: var(--spacing-2);
  border-top: 1px solid var(--alpha-overlay-light);
}
</style>
