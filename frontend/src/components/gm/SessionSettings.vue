<template>
  <BasePanel variant="elevated" class="session-settings">
    <template #header>
      <h3 class="panel-title">Настройки сессии</h3>
    </template>
    <div class="settings-content">
      <div class="stats">
        <div class="stat-item">
          <span class="stat-label">Игроков:</span>
          <span class="stat-value">{{ sessionStore.players.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Персонажей:</span>
          <span class="stat-value">{{ charactersStore.characters.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">NPC:</span>
          <span class="stat-value">{{ npcCount }}</span>
        </div>
      </div>
      <div class="actions">
        <BaseButton
          variant="secondary"
          :disabled="exporting"
          @click="handleExport"
        >
          <Download :size="16" />
          Экспортировать сессию
        </BaseButton>
        <BaseButton
          variant="secondary"
          :disabled="importing"
          @click="triggerFileInput"
        >
          <Upload :size="16" />
          Импортировать сессию
        </BaseButton>
        <input
          ref="fileInput"
          type="file"
          accept=".json"
          style="display: none"
          @change="handleImport"
        />
      </div>
    </div>
  </BasePanel>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Download, Upload } from 'lucide-vue-next'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { persistenceApi } from '@/services/api'
import { useToast } from '@/composables/useToast'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const toast = useToast()

const exporting = ref(false)
const importing = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const npcCount = computed(() => {
  const gmPlayer = sessionStore.players.find(p => p.is_gm)
  if (!gmPlayer) return 0
  return charactersStore.byPlayer(gmPlayer.id).length
})

async function handleExport() {
  if (!sessionStore.token) return
  
  exporting.value = true
  try {
    const blob = await persistenceApi.exportSessionDownload(sessionStore.token)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `dnd_session_${sessionStore.code}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    toast.success('Сессия экспортирована!')
  } catch (error: any) {
    console.error('Export failed:', error)
    toast.error(error.response?.data?.detail || 'Не удалось экспортировать сессию')
  } finally {
    exporting.value = false
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

async function handleImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  importing.value = true
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    
    // Валидация
    const validation = await persistenceApi.validateImport(data)
    if (!validation.is_valid) {
      toast.error('Файл невалиден: ' + validation.errors.join(', '))
      return
    }
    
    // Импорт
    const result = await persistenceApi.importSession(data)
    if (result.success) {
      toast.success(`Сессия импортирована! Код: ${result.session_code}`)
      // Обновить токен и перезагрузить данные
      if (result.gm_token) {
        sessionStore.token = result.gm_token
        sessionStore.isGm = true
        localStorage.setItem('token', result.gm_token)
        await sessionStore.fetchSessionState()
        await sessionStore.fetchPlayers()
        await charactersStore.fetchAll()
      }
    } else {
      toast.error('Ошибка импорта: ' + (result.errors?.join(', ') || 'Неизвестная ошибка'))
    }
  } catch (error: any) {
    console.error('Import failed:', error)
    toast.error('Не удалось импортировать сессию: ' + (error.message || 'Ошибка чтения файла'))
  } finally {
    importing.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
</script>

<style scoped>
.session-settings {
  width: 100%;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.stats {
  display: flex;
  gap: var(--spacing-6);
  padding: var(--spacing-4);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent-primary);
  font-family: var(--font-family-mono);
}

.actions {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}
</style>
