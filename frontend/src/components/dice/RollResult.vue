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

        <div class="result-main">
          <div class="dice-animation">🎲</div>
          <div class="result-value">{{ result.total }}</div>
          <div v-if="isCritical" class="result-label critical">Критический успех!</div>
          <div v-else-if="isFail" class="result-label fail">Критический провал!</div>
        </div>

        <div class="result-details">
          <div class="formula">{{ result.formula }}</div>
          <div v-if="result.rolls && result.rolls.length > 0" class="rolls">
            Броски: {{ result.rolls.join(', ') }}
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
let autoCloseTimer: number | null = null

// Auto-close after 1.5 seconds
onMounted(() => {
  autoCloseTimer = window.setTimeout(() => {
    handleClose()
  }, 1500)
})

onUnmounted(() => {
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
  }
})

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
  if (autoCloseTimer) {
    clearTimeout(autoCloseTimer)
  }

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
