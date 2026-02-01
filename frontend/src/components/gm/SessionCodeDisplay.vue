<template>
  <div class="session-code-display">
    <h2 class="title">Код сессии для подключения</h2>
    <div class="code-container">
      <div class="code">{{ sessionStore.code || '---' }}</div>
      <button class="copy-button" @click="copyCode" :disabled="!sessionStore.code">
        <Copy :size="20" />
        <span>Копировать</span>
      </button>
    </div>
    <p class="instructions">
      Поделитесь этим кодом с игроками. Они смогут подключиться к сессии, введя код на главной странице.
    </p>
  </div>
</template>

<script setup lang="ts">
import { Copy } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useToast } from '@/composables/useToast'

const sessionStore = useSessionStore()
const toast = useToast()

async function copyCode() {
  if (!sessionStore.code) return
  
  try {
    await navigator.clipboard.writeText(sessionStore.code)
    toast.success('Код скопирован в буфер обмена!')
  } catch (error) {
    // Fallback для старых браузеров
    const textArea = document.createElement('textarea')
    textArea.value = sessionStore.code
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      toast.success('Код скопирован в буфер обмена!')
    } catch (err) {
      toast.error('Не удалось скопировать код')
    }
    document.body.removeChild(textArea)
  }
}
</script>

<style scoped>
.session-code-display {
  text-align: center;
  padding: var(--spacing-8);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  margin-bottom: var(--spacing-6);
}

.title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-6) 0;
  color: var(--color-text-primary);
}

.code-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-4);
}

.code {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.2em;
  padding: var(--spacing-4) var(--spacing-8);
  background: var(--color-bg-tertiary);
  border: 2px solid var(--color-accent-primary);
  border-radius: var(--radius-lg);
  color: var(--color-accent-primary);
  box-shadow: var(--glow-accent);
}

.copy-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-accent-primary);
  color: var(--color-text-primary);
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-medium);
  transition: all var(--duration-fast);
}

.copy-button:hover:not(:disabled) {
  filter: brightness(1.1);
  box-shadow: var(--glow-accent);
}

.copy-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.instructions {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-relaxed);
}
</style>
