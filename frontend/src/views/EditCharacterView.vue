<template>
  <div class="edit-view">
    <!-- TopBar -->
    <div class="edit-topbar">
      <button class="back-btn" @click="router.push({ name: 'profile' })">
        &larr;
      </button>
      <h1 class="topbar-title">
        {{ character?.is_npc ? 'Редактировать NPC' : 'Редактировать персонажа' }}
      </h1>
    </div>

    <div v-if="loadingChar" class="loading-text">Загрузка...</div>

    <template v-else-if="character">
      <div class="edit-content">
        <!-- FlipCard preview -->
        <div class="card-area">
          <CharacterFlipCard :character="previewCharacter" />
        </div>

        <!-- Name -->
        <div class="form-section">
          <label class="field-label">Имя</label>
          <BaseInput v-model="form.name" placeholder="Имя персонажа" />
        </div>

        <!-- Appearance -->
        <div class="form-section">
          <label class="field-label">Описание внешности</label>
          <textarea
            class="appearance-textarea"
            v-model="form.appearance"
            placeholder="Опишите внешность: раса, телосложение, черты лица, одежда..."
            rows="3"
          ></textarea>
        </div>

        <!-- Regenerate avatar -->
        <BaseButton
          variant="secondary"
          size="lg"
          class="full-btn"
          :disabled="!form.appearance.trim() || generatingAvatar"
          @click="handleGenerateAvatar"
        >
          <span v-if="generatingAvatar" class="spinner"></span>
          <Sparkles v-else :size="20" />
          Перегенерировать аватар
        </BaseButton>
        <p v-if="!form.appearance.trim()" class="avatar-hint">
          Заполните описание внешности
        </p>

        <!-- Actions -->
        <div class="form-actions">
          <BaseButton
            variant="ghost"
            size="lg"
            class="full-btn"
            @click="router.push({ name: 'profile' })"
          >
            <X :size="20" />
            Отмена
          </BaseButton>
          <BaseButton
            variant="primary"
            size="lg"
            class="full-btn"
            :disabled="!canSubmit || submitting"
            @click="handleSubmit"
          >
            <Save :size="20" />
            Сохранить
          </BaseButton>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Sparkles, Save, X } from 'lucide-vue-next'
import type { UserCharacter } from '@/types/models'
import { userCharactersApi } from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import CharacterFlipCard from '@/components/profile/CharacterFlipCard.vue'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const character = ref<UserCharacter | null>(null)
const loadingChar = ref(true)
const submitting = ref(false)
const generatingAvatar = ref(false)

const form = reactive({
  name: '',
  appearance: '',
})

const canSubmit = computed(() => form.name.trim().length >= 1)

const previewCharacter = computed<UserCharacter>(() => {
  if (!character.value) return {} as UserCharacter
  return {
    ...character.value,
    name: form.name || character.value.name,
  }
})

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    const char = await userCharactersApi.get(id)
    character.value = char
    form.name = char.name
    form.appearance = char.appearance || ''
  } catch (err: any) {
    toast.error('Персонаж не найден')
    router.push({ name: 'profile' })
  } finally {
    loadingChar.value = false
  }
})

async function handleSubmit() {
  if (!canSubmit.value || !character.value) return
  submitting.value = true
  try {
    await userCharactersApi.update(character.value.id, {
      name: form.name.trim(),
      appearance: form.appearance.trim() || null,
    })
    toast.success('Персонаж обновлен!')
    router.push({ name: 'profile' })
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось обновить персонажа')
  } finally {
    submitting.value = false
  }
}

async function handleGenerateAvatar() {
  if (!character.value || !form.appearance.trim()) return
  generatingAvatar.value = true
  try {
    if (form.appearance.trim() !== (character.value.appearance || '')) {
      await userCharactersApi.update(character.value.id, {
        appearance: form.appearance.trim(),
      })
    }
    const updated = await userCharactersApi.generateAvatar(character.value.id)
    character.value = updated
    toast.success('Аватар сгенерирован!')
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось сгенерировать аватар')
  } finally {
    generatingAvatar.value = false
  }
}
</script>

<style scoped>
.edit-view {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
  max-width: 480px;
  margin: 0 auto;
}

.edit-topbar {
  display: flex;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  gap: var(--spacing-3);
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  background: none;
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
  border-radius: var(--radius-md);
  -webkit-tap-highlight-color: transparent;
}

.back-btn:active {
  background: var(--alpha-overlay-medium);
}

.topbar-title {
  flex: 1;
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.loading-text {
  text-align: center;
  color: var(--color-text-secondary);
  padding: var(--spacing-8) 0;
}

.edit-content {
  flex: 1;
  padding: var(--spacing-2) var(--spacing-4) var(--spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.card-area {
  display: flex;
  justify-content: center;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.field-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.appearance-textarea {
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border, rgba(255,255,255,0.1));
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.appearance-textarea:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.full-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
}

.avatar-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
  margin: 0;
}

.form-actions {
  display: flex;
  gap: var(--spacing-3);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border, rgba(255,255,255,0.1));
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: var(--spacing-1);
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
