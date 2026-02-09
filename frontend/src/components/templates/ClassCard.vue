<template>
  <div
    :class="['class-card', `class-${template.id.toLowerCase()}`, { selected: isSelected }]"
    @click="$emit('select')"
  >
    <div class="card-top">
      <span class="hit-die-badge">{{ template.hit_die }}</span>
    </div>
    <div class="card-body">
      <h3 class="class-name">{{ template.name_ru }}</h3>
      <p class="class-desc">{{ template.description_ru }}</p>
      <div class="class-abilities">{{ template.primary_abilities.join(' · ') }}</div>
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
.class-card {
  aspect-ratio: 3 / 4;
  width: 100%;
  max-width: 260px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all var(--duration-fast);
  display: flex;
  flex-direction: column;
  background: var(--color-bg-elevated);
  -webkit-tap-highlight-color: transparent;
}

.class-card.selected {
  box-shadow: 0 0 20px var(--card-class-color, rgba(233, 69, 96, 0.4));
  border-color: var(--card-class-color, var(--color-accent-primary));
}

.card-top {
  height: 40%;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: var(--spacing-3);
}

.hit-die-badge {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  padding: var(--spacing-1) var(--spacing-2);
  background: rgba(0, 0, 0, 0.4);
  border-radius: var(--radius-sm);
  color: rgba(255, 255, 255, 0.9);
}

.card-body {
  flex: 1;
  padding: var(--spacing-3) var(--spacing-4) var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.class-name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: var(--line-height-tight);
}

.class-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-relaxed);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.class-abilities {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

/* Class-specific colors */
.class-card.class-fighter {
  --card-class-color: var(--color-class-fighter);
}
.class-card.class-wizard {
  --card-class-color: var(--color-class-wizard);
}
.class-card.class-rogue {
  --card-class-color: var(--color-class-rogue);
}
.class-card.class-cleric {
  --card-class-color: var(--color-class-cleric);
}
.class-card.class-barbarian {
  --card-class-color: var(--color-class-barbarian);
}
.class-card.class-ranger {
  --card-class-color: var(--color-class-ranger);
}
.class-card.class-paladin {
  --card-class-color: var(--color-class-paladin);
}
.class-card.class-bard {
  --card-class-color: var(--color-class-bard);
}
.class-card.class-druid {
  --card-class-color: var(--color-class-druid);
}
.class-card.class-monk {
  --card-class-color: var(--color-class-monk);
}
.class-card.class-sorcerer {
  --card-class-color: var(--color-class-sorcerer);
}
.class-card.class-warlock {
  --card-class-color: var(--color-class-warlock);
}

.class-card .card-top {
  background: linear-gradient(
    135deg,
    var(--card-class-color, var(--color-accent-primary)),
    transparent
  ), var(--color-bg-elevated);
}
</style>
