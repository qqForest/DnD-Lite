<template>
  <div
    :class="['template-card', `class-${template.id.toLowerCase()}`, { selected: isSelected }]"
    @click="$emit('select')"
  >
    <div class="template-header">
      <h4 class="template-name">{{ template.name_ru }}</h4>
      <span class="hit-die">{{ template.hit_die }}</span>
    </div>
    <p class="template-description">{{ template.description_ru }}</p>
    <div class="template-meta">
      <div class="primary-abilities">
        <span class="label">Основные:</span>
        <span class="abilities">{{ template.primary_abilities.join(', ') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ClassTemplateListItem } from '@/types/models'

defineProps<{
  template: ClassTemplateListItem
  isSelected?: boolean
}>()

defineEmits<{
  select: []
}>()
</script>

<style scoped>
.template-card {
  padding: var(--spacing-4);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--duration-fast);
  border-left: 4px solid var(--color-accent-primary);
}

.template-card:hover {
  background: var(--alpha-overlay-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.template-card.selected {
  border-color: var(--color-accent-primary);
  box-shadow: var(--glow-accent);
}

.template-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-2);
}

.template-name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0;
  color: var(--color-text-primary);
}

.hit-die {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--alpha-overlay-medium);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
}

.template-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-3) 0;
  line-height: var(--line-height-relaxed);
}

.template-meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.primary-abilities {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
}

.label {
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

.abilities {
  color: var(--color-text-secondary);
}

/* Цвета классов */
.template-card.class-fighter {
  border-left-color: var(--color-class-fighter);
}

.template-card.class-wizard {
  border-left-color: var(--color-class-wizard);
}

.template-card.class-rogue {
  border-left-color: var(--color-class-rogue);
}

.template-card.class-cleric {
  border-left-color: var(--color-class-cleric);
}

.template-card.class-barbarian {
  border-left-color: var(--color-class-barbarian);
}

.template-card.class-ranger {
  border-left-color: var(--color-class-ranger);
}

.template-card.class-paladin {
  border-left-color: var(--color-class-paladin);
}

.template-card.class-bard {
  border-left-color: var(--color-class-bard);
}

.template-card.class-druid {
  border-left-color: var(--color-class-druid);
}

.template-card.class-monk {
  border-left-color: var(--color-class-monk);
}

.template-card.class-sorcerer {
  border-left-color: var(--color-class-sorcerer);
}

.template-card.class-warlock {
  border-left-color: var(--color-class-warlock);
}
</style>
