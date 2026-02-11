<template>
  <div
    :class="['class-card', `class-${template.id.toLowerCase()}`, { flipped }]"
    @click="flipped = !flipped"
  >
    <div class="card-inner">
      <!-- Front -->
      <div class="card-front">
        <div class="card-top">
          <span class="hit-die-badge">{{ template.hit_die }}</span>
        </div>

        <!-- AC Shield -->
        <div v-if="details" class="ac-shield">
          <svg viewBox="0 0 40 46" class="ac-shield-svg">
            <path
              d="M20 2 L38 10 L38 24 C38 34 28 42 20 44 C12 42 2 34 2 24 L2 10 Z"
              fill="var(--color-bg-secondary, #1a1a2e)"
              stroke="var(--card-class-color, #c0a46c)"
              stroke-width="2"
            />
          </svg>
          <span class="ac-shield-value">{{ details.recommended_ac }}</span>
        </div>

        <div class="card-body">
          <h3 class="class-name">{{ template.name_ru }}</h3>
          <p class="class-desc">{{ template.description_ru }}</p>

          <div v-if="details" class="modifier-chips">
            <span
              v-for="mod in primaryModifiers"
              :key="mod.label"
              class="modifier-chip"
            >{{ mod.label }} {{ mod.value }}</span>
          </div>
          <div v-else class="class-abilities">{{ template.primary_abilities.join(' · ') }}</div>
        </div>
      </div>

      <!-- Back -->
      <div class="card-back">
        <div class="back-header">
          <div class="back-name">{{ template.name_ru }}</div>
          <div class="back-subtitle">{{ template.hit_die }}{{ details ? ` · AC ${details.recommended_ac}` : '' }}</div>
        </div>

        <div v-if="details" class="stats-grid">
          <div v-for="stat in allStats" :key="stat.key" class="stat-cell">
            <span class="stat-label">{{ stat.label }}</span>
            <span class="stat-value">{{ stat.score }}</span>
            <span class="stat-mod" :class="{ positive: stat.mod >= 0 }">{{ formatMod(stat.mod) }}</span>
          </div>
        </div>
        <div v-else class="stats-loading">Загрузка...</div>

        <div v-if="details" class="back-footer">
          <div class="footer-item">
            <Heart :size="14" class="hp-icon" />
            <span>{{ details.recommended_hp }} HP</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Heart } from 'lucide-vue-next'
import type { ClassTemplateListItem, ClassTemplateResponse } from '@/types/models'

const props = defineProps<{
  template: ClassTemplateListItem
  details?: ClassTemplateResponse
}>()

const flipped = ref(false)

const abilityLabels: Record<string, string> = {
  strength: 'СИЛ',
  dexterity: 'ЛОВ',
  constitution: 'ТЕЛ',
  intelligence: 'ИНТ',
  wisdom: 'МДР',
  charisma: 'ХАР',
}

function calcMod(score: number): number {
  return Math.floor((score - 10) / 2)
}

function formatMod(mod: number): string {
  return mod >= 0 ? `+${mod}` : `${mod}`
}

const primaryModifiers = computed(() => {
  if (!props.details) return []
  return props.template.primary_abilities.map(key => {
    const score = (props.details as any)[key] as number ?? 10
    const mod = calcMod(score)
    return {
      label: abilityLabels[key] ?? key,
      value: formatMod(mod),
    }
  })
})

const allStats = computed(() => {
  if (!props.details) return []
  const keys = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const
  return keys.map(key => {
    const score = props.details![key]
    return {
      key,
      label: abilityLabels[key],
      score,
      mod: calcMod(score),
    }
  })
})
</script>

<style scoped>
.class-card {
  perspective: 1000px;
  aspect-ratio: 3 / 4;
  width: 100%;
  max-width: 260px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 300ms ease;
}

.class-card.flipped .card-inner {
  transform: rotateY(180deg);
}

.card-front,
.card-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* Front */
.card-front {
  display: flex;
  flex-direction: column;
  background: var(--color-bg-elevated);
}

.card-top {
  height: 40%;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: var(--spacing-3);
  background: linear-gradient(
    135deg,
    var(--card-class-color, var(--color-accent-primary)),
    transparent
  ), var(--color-bg-elevated);
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

.ac-shield {
  position: absolute;
  top: var(--spacing-2);
  left: var(--spacing-2);
  z-index: 3;
  width: 50px;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ac-shield-svg {
  position: absolute;
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.6));
}

.ac-shield-value {
  position: relative;
  font-family: var(--font-family-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--card-class-color, #c0a46c);
  line-height: 1;
  margin-top: -2px;
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

.modifier-chips {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.modifier-chip {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--alpha-overlay-medium);
  color: var(--card-class-color, var(--color-text-primary));
}

/* Back */
.card-back {
  transform: rotateY(180deg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border, rgba(255,255,255,0.1));
  display: flex;
  flex-direction: column;
  padding: var(--spacing-3);
  gap: var(--spacing-2);
}

.back-header {
  text-align: center;
}

.back-name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.back-subtitle {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-1);
  flex: 1;
  align-content: center;
}

.stats-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.stat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-1) 2px;
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
}

.stat-label {
  font-family: var(--font-family-display);
  font-size: 10px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.stat-value {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1;
}

.stat-mod {
  font-family: var(--font-family-mono);
  font-size: 10px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.stat-mod.positive {
  color: var(--color-success, #4ade80);
}

.back-footer {
  display: flex;
  justify-content: center;
  gap: var(--spacing-2);
}

.footer-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-primary);
}

.hp-icon {
  color: var(--color-danger, #ef4444);
}

/* Class-specific colors */
.class-card.class-fighter { --card-class-color: var(--color-class-fighter); }
.class-card.class-wizard { --card-class-color: var(--color-class-wizard); }
.class-card.class-rogue { --card-class-color: var(--color-class-rogue); }
.class-card.class-cleric { --card-class-color: var(--color-class-cleric); }
.class-card.class-barbarian { --card-class-color: var(--color-class-barbarian); }
.class-card.class-ranger { --card-class-color: var(--color-class-ranger); }
.class-card.class-paladin { --card-class-color: var(--color-class-paladin); }
.class-card.class-bard { --card-class-color: var(--color-class-bard); }
.class-card.class-druid { --card-class-color: var(--color-class-druid); }
.class-card.class-monk { --card-class-color: var(--color-class-monk); }
.class-card.class-sorcerer { --card-class-color: var(--color-class-sorcerer); }
.class-card.class-warlock { --card-class-color: var(--color-class-warlock); }
</style>
