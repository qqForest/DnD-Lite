<template>
  <div class="flip-card" :class="{ flipped, compact }" @click="flipped = !flipped">
    <div class="flip-card-inner">
      <!-- Front -->
      <div class="flip-card-front">
        <img
          v-if="character.avatar_url"
          :src="character.avatar_url"
          alt=""
          class="card-bg"
        />
        <div v-else class="card-bg-placeholder">
          <User :size="64" :stroke-width="1" />
        </div>

        <span v-if="character.is_npc" class="npc-badge">NPC</span>

        <div class="card-bottom-gradient">
          <div class="card-name">{{ character.name }}</div>
          <div class="card-subtitle">
            <span v-if="character.class_name">{{ character.class_name }}</span>
            <span>Ур. {{ character.level }}</span>
          </div>
        </div>
      </div>

      <!-- Back -->
      <div class="flip-card-back">
        <div class="back-actions">
          <button
            v-if="editable"
            class="action-btn"
            title="Редактировать"
            @click.stop="$emit('edit')"
          >
            <Pencil :size="18" />
          </button>
          <button
            v-if="deletable"
            class="action-btn action-btn--danger"
            title="Удалить"
            @click.stop="$emit('delete')"
          >
            <Trash2 :size="18" />
          </button>
        </div>

        <div class="back-header">
          <div class="back-name">{{ character.name }}</div>
          <div class="back-subtitle">
            <span v-if="character.class_name">{{ character.class_name }}</span>
            <span>Ур. {{ character.level }}</span>
          </div>
        </div>

        <div class="stats-grid">
          <div v-for="stat in stats" :key="stat.key" class="stat-cell">
            <span class="stat-label">{{ stat.label }}</span>
            <span class="stat-value">{{ (character as any)[stat.key] }}</span>
          </div>
        </div>

        <div class="hp-section">
          <div class="hp-header">
            <Heart :size="16" class="hp-icon" />
            <span class="hp-text">{{ character.current_hp }} / {{ character.max_hp }}</span>
          </div>
          <div class="hp-bar-track">
            <div class="hp-bar-fill" :style="{ width: hpPercent + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { User, Pencil, Trash2, Heart } from 'lucide-vue-next'
import type { UserCharacter } from '@/types/models'

const props = defineProps<{
  character: UserCharacter
  deletable?: boolean
  editable?: boolean
  compact?: boolean
}>()

defineEmits<{
  delete: []
  edit: []
}>()

const flipped = ref(false)

const hpPercent = computed(() => {
  if (props.character.max_hp <= 0) return 0
  return Math.min(100, Math.max(0, (props.character.current_hp / props.character.max_hp) * 100))
})

const stats = [
  { key: 'strength', label: 'СИЛ' },
  { key: 'dexterity', label: 'ЛОВ' },
  { key: 'constitution', label: 'ТЕЛ' },
  { key: 'intelligence', label: 'ИНТ' },
  { key: 'wisdom', label: 'МДР' },
  { key: 'charisma', label: 'ХАР' },
]
</script>

<style scoped>
.flip-card {
  perspective: 1000px;
  aspect-ratio: 3 / 4;
  width: 100%;
  max-width: 300px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 300ms ease;
}

.flip-card.flipped .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* Front */
.flip-card-front {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.card-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-bg-placeholder {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    var(--color-bg-secondary),
    var(--color-bg-elevated, var(--color-bg-secondary))
  );
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted, var(--color-text-secondary));
  opacity: 0.5;
}

.npc-badge {
  position: absolute;
  top: var(--spacing-3);
  left: var(--spacing-3);
  font-size: var(--font-size-xs);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-warning, #f59e0b);
  color: #000;
  font-weight: 600;
  z-index: 2;
}

.card-bottom-gradient {
  position: relative;
  z-index: 1;
  padding: var(--spacing-6) var(--spacing-4) var(--spacing-4);
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent);
}

.card-name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: #fff;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
  line-height: 1.2;
}

.card-subtitle {
  display: flex;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.75);
  margin-top: var(--spacing-1);
}

/* Back */
.flip-card-back {
  transform: rotateY(180deg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: var(--spacing-4);
  gap: var(--spacing-3);
}

.back-actions {
  display: flex;
  gap: var(--spacing-2);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  border-radius: var(--radius-md);
  background: var(--alpha-overlay-medium, rgba(255, 255, 255, 0.1));
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
  border: none;
}

.action-btn:hover {
  background: var(--alpha-overlay-light);
  color: var(--color-text-primary);
}

.action-btn--danger:hover {
  color: var(--color-danger, #ef4444);
}

.back-header {
  text-align: center;
}

.back-name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.back-subtitle {
  display: flex;
  justify-content: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-2);
  flex: 1;
  align-content: center;
}

.stat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-2);
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
}

.stat-label {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.stat-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text-primary);
}

.hp-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.hp-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.hp-icon {
  color: var(--color-danger, #ef4444);
}

.hp-text {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.hp-bar-track {
  height: 6px;
  background: var(--color-bg-primary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.hp-bar-fill {
  height: 100%;
  background: var(--color-danger, #ef4444);
  border-radius: var(--radius-full);
  transition: width 300ms ease;
}

/* Compact mode */
.flip-card.compact {
  max-width: 120px;
}

.flip-card.compact .card-name {
  font-size: var(--font-size-sm);
}

.flip-card.compact .card-subtitle {
  font-size: 10px;
}

.flip-card.compact .card-bottom-gradient {
  padding: var(--spacing-3) var(--spacing-2) var(--spacing-2);
}

.flip-card.compact .flip-card-back {
  padding: var(--spacing-2);
  gap: var(--spacing-1);
}

.flip-card.compact .back-actions {
  display: none;
}

.flip-card.compact .back-name {
  font-size: var(--font-size-sm);
}

.flip-card.compact .back-subtitle {
  font-size: 10px;
}

.flip-card.compact .stats-grid {
  gap: 2px;
}

.flip-card.compact .stat-cell {
  padding: var(--spacing-1);
}

.flip-card.compact .stat-label {
  font-size: 9px;
}

.flip-card.compact .stat-value {
  font-size: var(--font-size-sm);
}

.flip-card.compact .hp-bar-track {
  height: 4px;
}

.flip-card.compact .hp-text {
  font-size: 10px;
}

.flip-card.compact .hp-icon {
  width: 12px;
  height: 12px;
}
</style>
