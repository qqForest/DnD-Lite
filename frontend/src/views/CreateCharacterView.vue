<template>
  <div class="wizard-view">
    <!-- TopBar -->
    <div class="wizard-topbar">
      <button class="back-btn" @click="handleBack">
        &larr;
      </button>
      <h1 class="topbar-title">{{ isNpc ? 'Новый NPC' : 'Новый персонаж' }}</h1>
      <span class="step-label">{{ currentStep }} / 3</span>
    </div>

    <!-- Step dots -->
    <div class="step-dots">
      <span
        v-for="s in 3"
        :key="s"
        class="step-dot"
        :class="{ active: s <= currentStep }"
      />
    </div>

    <!-- Step 1: Class selection -->
    <div v-if="currentStep === 1" class="step-content">
      <div v-if="loadingTemplates" class="loading-text">Загрузка...</div>
      <template v-else>
        <TemplateCarousel
          ref="carouselRef"
          :templates="templates"
          :current-details="currentTemplateDetails ?? undefined"
        />

        <div class="form-section">
          <label class="field-label">Имя персонажа</label>
          <BaseInput
            v-model="characterName"
            placeholder="Введите имя"
          />
        </div>

        <div class="step-actions">
          <BaseButton
            variant="primary"
            size="lg"
            class="full-btn"
            :disabled="!canProceedStep1"
            @click="goToStep2"
          >
            Далее
          </BaseButton>
        </div>
      </template>
    </div>

    <!-- Step 2: Avatar -->
    <div v-if="currentStep === 2" class="step-content">
      <div class="avatar-preview-area">
        <div class="avatar-card">
          <img
            v-if="avatarUrl"
            :src="avatarUrl"
            alt="Аватар"
            class="avatar-image"
          />
          <div v-else class="avatar-placeholder">
            <User :size="48" :stroke-width="1" />
          </div>
        </div>
      </div>

      <div class="form-section">
        <label class="field-label">Описание портрета</label>
        <textarea
          class="appearance-textarea"
          v-model="appearance"
          placeholder="Опишите внешность: раса, телосложение, черты лица, одежда..."
          rows="3"
        ></textarea>
      </div>

      <div class="step-actions">
        <BaseButton
          variant="primary"
          size="lg"
          class="full-btn"
          :disabled="!appearance.trim() || generatingAvatar"
          @click="handleGenerate"
        >
          <span v-if="generatingAvatar" class="spinner"></span>
          <Sparkles v-else :size="20" />
          {{ generatingAvatar ? 'Генерация...' : 'Сгенерировать' }}
        </BaseButton>
        <button class="skip-link" @click="handleSkip">
          Пропустить
        </button>
      </div>

      <div v-if="avatarUrl" class="step-actions">
        <BaseButton
          variant="primary"
          size="lg"
          class="full-btn"
          @click="currentStep = 3"
        >
          Далее
        </BaseButton>
      </div>
    </div>

    <!-- Step 3: Preview -->
    <div v-if="currentStep === 3" class="step-content">
      <div class="preview-area">
        <CharacterFlipCard
          v-if="createdCharacter"
          :character="createdCharacter"
        />
      </div>

      <div class="preview-name" v-if="createdCharacter">
        {{ createdCharacter.name }}
      </div>

      <div class="step-actions">
        <BaseButton
          variant="primary"
          size="lg"
          class="full-btn"
          @click="handleDone"
        >
          <Check :size="20" />
          Готово
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Sparkles, Check } from 'lucide-vue-next'
import { templatesApi, userCharactersApi } from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import TemplateCarousel from '@/components/templates/TemplateCarousel.vue'
import CharacterFlipCard from '@/components/profile/CharacterFlipCard.vue'
import type { ClassTemplateListItem, ClassTemplateResponse, UserCharacter } from '@/types/models'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const isNpc = computed(() => route.query.npc === 'true')

const currentStep = ref(1)
const templates = ref<ClassTemplateListItem[]>([])
const loadingTemplates = ref(true)
const carouselRef = ref<InstanceType<typeof TemplateCarousel> | null>(null)
const detailsCache = ref<Record<string, ClassTemplateResponse>>({})
const currentTemplateDetails = ref<ClassTemplateResponse | null>(null)
const characterName = ref('')
const appearance = ref('')
const createdCharacter = ref<UserCharacter | null>(null)
const generatingAvatar = ref(false)
const avatarUrl = ref<string | null>(null)

const currentTemplateId = computed(() => {
  const idx = carouselRef.value?.currentIndex ?? 0
  return templates.value[idx]?.id ?? null
})

const canProceedStep1 = computed(() => {
  return templates.value.length > 0 && characterName.value.trim().length >= 1
})

onMounted(async () => {
  try {
    templates.value = await templatesApi.list()
  } catch (err) {
    toast.error('Не удалось загрузить шаблоны')
  } finally {
    loadingTemplates.value = false
  }
})

watch(currentTemplateId, async (id) => {
  if (!id) {
    currentTemplateDetails.value = null
    return
  }
  if (detailsCache.value[id]) {
    currentTemplateDetails.value = detailsCache.value[id]
    return
  }
  try {
    const details = await templatesApi.get(id)
    detailsCache.value[id] = details
    currentTemplateDetails.value = details
  } catch (err) {
    console.error('Failed to load template:', err)
  }
})

async function goToStep2() {
  if (!canProceedStep1.value) return
  // Убедимся что детали текущего шаблона загружены
  const id = currentTemplateId.value
  if (id && !detailsCache.value[id]) {
    try {
      const details = await templatesApi.get(id)
      detailsCache.value[id] = details
      currentTemplateDetails.value = details
    } catch (err) {
      toast.error('Не удалось загрузить шаблон')
      return
    }
  }
  currentStep.value = 2
}

async function createCharacter(): Promise<UserCharacter | null> {
  if (!currentTemplateDetails.value) return null

  const tmpl = currentTemplateDetails.value
  try {
    const char = await userCharactersApi.create({
      name: characterName.value.trim(),
      class_name: tmpl.name_ru,
      level: 1,
      is_npc: isNpc.value,
      strength: tmpl.strength,
      dexterity: tmpl.dexterity,
      constitution: tmpl.constitution,
      intelligence: tmpl.intelligence,
      wisdom: tmpl.wisdom,
      charisma: tmpl.charisma,
      max_hp: tmpl.recommended_hp,
      current_hp: tmpl.recommended_hp,
      armor_class: tmpl.recommended_ac,
      appearance: appearance.value.trim() || null,
    })
    return char
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось создать персонажа')
    return null
  }
}

async function handleGenerate() {
  if (!appearance.value.trim()) return
  generatingAvatar.value = true

  try {
    if (!createdCharacter.value) {
      const char = await createCharacter()
      if (!char) return
      createdCharacter.value = char
    } else {
      await userCharactersApi.update(createdCharacter.value.id, {
        appearance: appearance.value.trim(),
      })
    }

    const updated = await userCharactersApi.generateAvatar(createdCharacter.value!.id)
    createdCharacter.value = updated
    avatarUrl.value = updated.avatar_url
    toast.success('Аватар сгенерирован!')
  } catch (err: any) {
    toast.error(err.response?.data?.detail || 'Не удалось сгенерировать аватар')
  } finally {
    generatingAvatar.value = false
  }
}

async function handleSkip() {
  if (!createdCharacter.value) {
    const char = await createCharacter()
    if (!char) return
    createdCharacter.value = char
  }
  currentStep.value = 3
}

function handleDone() {
  toast.success(isNpc.value ? 'NPC создан!' : 'Персонаж создан!')
  router.push({ name: 'profile' })
}

function handleBack() {
  if (currentStep.value > 1) {
    currentStep.value--
  } else {
    router.push({ name: 'profile' })
  }
}
</script>

<style scoped>
.wizard-view {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
  max-width: 480px;
  margin: 0 auto;
}

.wizard-topbar {
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

.step-label {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.step-dots {
  display: flex;
  gap: var(--spacing-2);
  justify-content: center;
  padding-bottom: var(--spacing-4);
}

.step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  opacity: 0.3;
  transition: all 200ms ease;
}

.step-dot.active {
  opacity: 1;
  background: var(--color-accent-primary);
  box-shadow: var(--glow-accent);
}

.step-content {
  flex: 1;
  padding: 0 var(--spacing-4) var(--spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.loading-text {
  text-align: center;
  color: var(--color-text-secondary);
  padding: var(--spacing-8) 0;
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

.avatar-preview-area {
  display: flex;
  justify-content: center;
}

.avatar-card {
  width: 200px;
  aspect-ratio: 3 / 4;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border, rgba(255,255,255,0.1));
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  opacity: 0.5;
}

.step-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-3);
}

.full-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
}

.skip-link {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  padding: var(--spacing-2);
  min-height: 44px;
  -webkit-tap-highlight-color: transparent;
}

.skip-link:active {
  color: var(--color-text-primary);
}

.preview-area {
  display: flex;
  justify-content: center;
  flex: 1;
}

.preview-name {
  text-align: center;
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
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
