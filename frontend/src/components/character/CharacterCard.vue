<template>
  <div :class="['character-card', classTypeClass]" @click="$emit('click')">
    <div class="character-avatar">
      <img v-if="avatarSrc" :src="avatarSrc" :alt="character.name" />
      <span v-else class="avatar-placeholder">{{ initials }}</span>
    </div>
    <div class="character-info">
      <h4 class="character-name">{{ character.name }}</h4>
      <p class="character-meta">
        <span v-if="character.class_name">{{ className }}</span>
        <span v-if="character.class_name && character.level"> • </span>
        <span v-if="character.level">Уровень {{ character.level }}</span>
      </p>
      <HPBar :current="character.current_hp" :max="character.max_hp" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Character } from '@/types/models'
import HPBar from './HPBar.vue'

const props = defineProps<{
  character: Character
  avatar?: string
}>()

defineEmits<{
  click: []
}>()

const avatarSrc = computed(() => {
  return props.avatar || (props.character as any).avatar_url || null
})

const initials = computed(() => {
  return props.character.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const className = computed(() => {
  const classMap: Record<string, string> = {
    Fighter: 'Воин',
    Wizard: 'Волшебник',
    Rogue: 'Плут',
    Cleric: 'Жрец',
    Barbarian: 'Варвар',
    Ranger: 'Следопыт',
    Paladin: 'Паладин',
    Bard: 'Бард',
    Druid: 'Друид',
    Monk: 'Монах',
    Sorcerer: 'Чародей',
    Warlock: 'Колдун'
  }
  return classMap[props.character.class_name || ''] || props.character.class_name || ''
})

const classTypeClass = computed(() => {
  if (!props.character.class_name) return ''
  return `class-${props.character.class_name.toLowerCase()}`
})
</script>

<style scoped>
.character-card {
  display: flex;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-accent-primary);
  transition: all var(--duration-fast);
  cursor: pointer;
}

.character-card:hover {
  background: var(--alpha-overlay-light);
  transform: translateX(4px);
}

.character-card.class-fighter {
  border-left-color: var(--color-class-fighter);
}

.character-card.class-wizard {
  border-left-color: var(--color-class-wizard);
}

.character-card.class-rogue {
  border-left-color: var(--color-class-rogue);
}

.character-card.class-cleric {
  border-left-color: var(--color-class-cleric);
}

.character-card.class-barbarian {
  border-left-color: var(--color-class-barbarian);
}

.character-card.class-ranger {
  border-left-color: var(--color-class-ranger);
}

.character-card.class-paladin {
  border-left-color: var(--color-class-paladin);
}

.character-card.class-bard {
  border-left-color: var(--color-class-bard);
}

.character-card.class-druid {
  border-left-color: var(--color-class-druid);
}

.character-card.class-monk {
  border-left-color: var(--color-class-monk);
}

.character-card.class-sorcerer {
  border-left-color: var(--color-class-sorcerer);
}

.character-card.class-warlock {
  border-left-color: var(--color-class-warlock);
}

.character-avatar {
  width: var(--avatar-size-md);
  height: var(--avatar-size-md);
  border-radius: var(--radius-full);
  overflow: hidden;
  flex-shrink: 0;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: var(--color-accent-secondary);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.character-info {
  flex: 1;
  min-width: 0;
}

.character-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-1) 0;
}

.character-meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-2) 0;
}
</style>
