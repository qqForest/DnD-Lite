<template>
  <div class="dice-selector">
    <button
      v-for="dice in diceTypes"
      :key="dice"
      :class="['dice-button', { active: selectedDice === dice }]"
      @click="selectDice(dice)"
    >
      <span class="dice-label">{{ dice }}</span>
    </button>
    <div class="custom-roll">
      <input
        v-model="customNotation"
        type="text"
        placeholder="2d6+3"
        class="custom-input"
        @keyup.enter="rollCustom"
      />
      <button class="roll-button" @click="rollCustom">
        Бросить
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDiceStore } from '@/stores/dice'

const diceStore = useDiceStore()
const selectedDice = ref<string | null>(null)
const customNotation = ref('')

const diceTypes = ['d4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100']

function selectDice(dice: string) {
  selectedDice.value = dice
  rollDice(dice)
}

async function rollDice(notation: string) {
  try {
    await diceStore.rollDice(notation)
  } catch (error) {
    console.error('Failed to roll dice:', error)
  }
}

async function rollCustom() {
  if (!customNotation.value.trim()) return
  try {
    await diceStore.rollDice(customNotation.value.trim())
    customNotation.value = ''
  } catch (error) {
    console.error('Failed to roll custom dice:', error)
  }
}
</script>

<style scoped>
.dice-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.dice-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2);
  background: var(--color-bg-elevated);
  border: 2px solid transparent;
  border-radius: var(--radius-md);
  min-width: 56px;
  min-height: 56px;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.dice-button:hover {
  background: var(--alpha-overlay-medium);
  transform: translateY(-2px);
}

.dice-button.active {
  border-color: var(--color-accent-primary);
  box-shadow: var(--glow-accent);
}

.dice-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  color: var(--color-text-primary);
}

.custom-roll {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-left: var(--spacing-4);
}

.custom-input {
  width: 120px;
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--alpha-overlay-medium);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
}

.custom-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.roll-button {
  padding: var(--spacing-2) var(--spacing-4);
  background: var(--color-accent-primary);
  color: var(--color-text-primary);
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-medium);
  transition: all var(--duration-fast);
}

.roll-button:hover {
  filter: brightness(1.1);
}
</style>
