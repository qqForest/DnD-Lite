<template>
  <div class="ready-button-container">
    <BaseButton
      :variant="sessionStore.isReady ? 'primary' : 'secondary'"
      size="lg"
      :disabled="!canBeReady || setting"
      @click="toggleReady"
      class="ready-button"
    >
      <CheckCircle v-if="sessionStore.isReady" :size="24" />
      <Circle v-else :size="24" />
      <span>{{ setting ? 'Обновление...' : sessionStore.isReady ? 'Готов' : 'Не готов' }}</span>
    </BaseButton>
    <p v-if="!charactersStore.selectedId" class="hint">
      Выберите персонажа, чтобы отметить готовность
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CheckCircle, Circle } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'

const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const toast = useToast()

const setting = ref(false)

const canBeReady = computed(() => {
  return charactersStore.selectedId !== null
})

async function toggleReady() {
  if (!canBeReady.value || setting.value) return
  
  setting.value = true
  try {
    await sessionStore.setReady(!sessionStore.isReady)
    toast.success(sessionStore.isReady ? 'Вы готовы!' : 'Статус готовности снят')
  } catch (error: any) {
    console.error('Failed to set ready status:', error)
    toast.error(error.response?.data?.detail || 'Не удалось изменить статус готовности')
  } finally {
    setting.value = false
  }
}
</script>

<style scoped>
.ready-button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
}

.ready-button {
  min-width: 200px;
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-3);
}

.hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  text-align: center;
  margin: 0;
}
</style>
