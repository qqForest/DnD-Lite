<template>
  <Transition name="modal">
    <div
      v-if="!isClosing"
      :class="['roll-result-overlay', { critical: isCritical, fail: isFail }]"
      @click.self="handleClose"
    >
      <div class="roll-result-card">
        <div class="result-header">
          <span class="roller-name">{{ result.player_name }}</span>
          <button class="close-btn" @click="handleClose">×</button>
        </div>

        <div v-if="isAdvantageRoll" class="roll-type-badge" :class="result.roll_type">
          {{ result.roll_type === 'advantage' ? '⬆ Преимущество' : '⬇ Помеха' }}
        </div>

        <div class="result-main">
          <div v-if="isAdvantageRoll && result.all_rolls" class="advantage-rolls">
            <div
              v-for="(rollSet, idx) in result.all_rolls"
              :key="idx"
              :class="[
                'advantage-die',
                {
                  chosen: revealed && idx === result.chosen_index,
                  discarded: revealed && idx !== result.chosen_index,
                  rolling: !revealed
                }
              ]"
            >
              <div :class="['die-emoji', { spinning: !revealed }]">🎲</div>
              <div v-if="revealed" class="die-value pop-in">{{ rollSetTotal(rollSet) }}</div>
              <div v-else class="die-value rolling-placeholder">?</div>
              <div class="die-rolls" v-if="revealed && rollSet.length > 1">{{ rollSet.join(' + ') }}</div>
              <div v-if="revealed" class="die-tag pop-in">{{ idx === result.chosen_index ? '✓' : '✗' }}</div>
            </div>
          </div>
          <div v-else :class="['dice-animation', { spinning: !revealed }]">🎲</div>
          <div v-if="revealed" class="result-value pop-in">{{ result.total }}</div>
          <div v-else class="result-value rolling-placeholder">?</div>
          <div v-if="revealed && isCritical" class="result-label critical pop-in">Критический успех!</div>
          <div v-else-if="revealed && isFail" class="result-label fail pop-in">Критический провал!</div>
        </div>

        <div class="result-details">
          <div class="formula">{{ result.formula }}</div>
          <div v-if="!isAdvantageRoll && result.rolls && result.rolls.length > 0" class="rolls">
            Броски: {{ result.rolls.join(', ') }}
          </div>
          <div v-if="isAdvantageRoll && result.modifier" class="rolls">
            Модификатор: {{ result.modifier > 0 ? '+' : '' }}{{ result.modifier }}
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { DiceResult } from '@/types/models'

const props = defineProps<{
  result: DiceResult
}>()

const emit = defineEmits<{
  close: []
}>()

const isClosing = ref(false)
const revealed = ref(false)
let autoCloseTimer: number | null = null
let revealTimer: number | null = null

const ROLL_DURATION = 1200 // время кручения кубиков (мс)
const SHOW_NORMAL = 2500   // время показа результата обычного броска
const SHOW_ADVANTAGE = 4000 // время показа результата advantage/disadvantage

onMounted(() => {
  // Фаза кручения
  revealTimer = window.setTimeout(() => {
    revealed.value = true
  }, ROLL_DURATION)

  // Автозакрытие после раскрытия
  const totalDelay = ROLL_DURATION + (isAdvantageRoll.value ? SHOW_ADVANTAGE : SHOW_NORMAL)
  autoCloseTimer = window.setTimeout(() => {
    handleClose()
  }, totalDelay)
})

onUnmounted(() => {
  if (autoCloseTimer) clearTimeout(autoCloseTimer)
  if (revealTimer) clearTimeout(revealTimer)
})

const isAdvantageRoll = computed(() => {
  return props.result.roll_type === 'advantage' || props.result.roll_type === 'disadvantage'
})

function rollSetTotal(rollSet: number[]): number {
  return rollSet.reduce((a, b) => a + b, 0)
}

const isCritical = computed(() => {
  if (props.result.rolls && props.result.rolls.length === 1) {
    const roll = props.result.rolls[0]
    return roll === 20 || (props.result.formula.includes('d') && roll === getDiceMax())
  }
  return false
})

const isFail = computed(() => {
  if (props.result.rolls && props.result.rolls.length === 1) {
    return props.result.rolls[0] === 1
  }
  return false
})

function getDiceMax(): number {
  const match = props.result.formula.match(/d(\d+)/)
  return match ? parseInt(match[1]) : 0
}

function handleClose() {
  if (autoCloseTimer) clearTimeout(autoCloseTimer)
  if (revealTimer) clearTimeout(revealTimer)

  // Показываем результат если ещё не раскрыт
  revealed.value = true

  // Запускаем анимацию закрытия
  isClosing.value = true

  // Эмитим close после завершения анимации (300ms)
  setTimeout(() => {
    emit('close')
  }, 300)
}
</script>

<style scoped>
.roll-result-overlay {
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

.roll-result-card {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-xl);
  min-width: 320px;
  max-width: 90vw;
  animation: slideIn var(--duration-normal) var(--ease-bounce);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.roller-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: var(--font-size-2xl);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast);
}

.close-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.result-main {
  text-align: center;
  padding: var(--spacing-6) 0;
}

.dice-animation {
  font-size: 64px;
  margin-bottom: var(--spacing-4);
  animation: spin 0.5s ease-out;
}

.dice-animation.spinning {
  animation: continuousSpin 0.4s linear infinite;
}

.rolling-placeholder {
  opacity: 0.4;
  animation: pulse 0.6s ease-in-out infinite;
}

.pop-in {
  animation: popIn 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.result-value {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.result-label {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-top: var(--spacing-2);
}

.result-label.critical {
  color: var(--color-accent-gold);
  text-shadow: 0 0 10px var(--color-accent-gold);
}

.result-label.fail {
  color: var(--color-danger);
}

.result-details {
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--alpha-overlay-light);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  text-align: center;
}

.formula {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.rolls {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Roll type badge */
.roll-type-badge {
  text-align: center;
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-2);
}

.roll-type-badge.advantage {
  background: rgba(255, 215, 0, 0.15);
  color: var(--color-accent-gold, #ffd700);
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.roll-type-badge.disadvantage {
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-danger, #ef4444);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Advantage/Disadvantage dual dice */
.advantage-rolls {
  display: flex;
  gap: var(--spacing-4);
  justify-content: center;
  align-items: center;
  margin-bottom: var(--spacing-3);
}

.advantage-die {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-lg);
  border: 2px solid transparent;
  transition: all var(--duration-fast);
  position: relative;
  min-width: 100px;
}

.advantage-die.chosen {
  border-color: var(--color-accent-gold, #ffd700);
  background: rgba(255, 215, 0, 0.1);
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.25);
  transform: scale(1.1);
}

.advantage-die.discarded {
  opacity: 0.4;
  filter: grayscale(60%);
  transform: scale(0.9);
}

.die-emoji {
  font-size: 40px;
  animation: spin 0.5s ease-out;
}

.die-emoji.spinning {
  animation: continuousSpin 0.4s linear infinite;
}

.advantage-die.rolling {
  border-color: var(--alpha-overlay-medium);
}

.die-value {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.advantage-die.discarded .die-value {
  text-decoration: line-through;
  color: var(--color-text-muted);
}

.die-rolls {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-family: var(--font-family-mono);
}

.die-tag {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  margin-top: var(--spacing-1);
}

.advantage-die.chosen .die-tag {
  color: var(--color-accent-gold, #ffd700);
}

.advantage-die.discarded .die-tag {
  color: var(--color-text-muted);
}

/* Critical/Fail effects */
.roll-result-overlay.critical .roll-result-card {
  background: linear-gradient(135deg,
    var(--color-bg-elevated) 0%,
    rgba(255, 215, 0, 0.1) 100%
  );
  box-shadow: 0 0 40px rgba(255, 215, 0, 0.3);
}

.roll-result-overlay.fail .roll-result-card {
  background: linear-gradient(135deg,
    var(--color-bg-elevated) 0%,
    rgba(239, 68, 68, 0.1) 100%
  );
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
  0% {
    transform: rotate(0deg) scale(0.5);
    opacity: 0;
  }
  50% {
    transform: rotate(180deg) scale(1.2);
  }
  100% {
    transform: rotate(360deg) scale(1);
    opacity: 1;
  }
}

@keyframes continuousSpin {
  0% { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(90deg) scale(1.15); }
  50% { transform: rotate(180deg) scale(1); }
  75% { transform: rotate(270deg) scale(1.15); }
  100% { transform: rotate(360deg) scale(1); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

@keyframes popIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  60% {
    transform: scale(1.15);
    opacity: 1;
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

.modal-enter-active .roll-result-card {
  animation: slideIn var(--duration-normal) var(--ease-bounce);
}

.modal-leave-active {
  transition: opacity var(--duration-normal) var(--ease-out);
}

.modal-leave-active .roll-result-card {
  transition: all var(--duration-normal) var(--ease-out);
}

.modal-leave-to {
  opacity: 0;
}

.modal-leave-to .roll-result-card {
  transform: scale(0.9) translateY(20px);
  opacity: 0;
}
</style>
