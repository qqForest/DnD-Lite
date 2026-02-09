<template>
  <div class="character-card" :class="{ selected, clickable }" @click="$emit('select')">
    <div class="card-header">
      <div class="card-title">
        <img
          v-if="character.avatar_url"
          :src="character.avatar_url"
          alt=""
          class="card-avatar"
        />
        <span class="name">{{ character.name }}</span>
        <span v-if="character.is_npc" class="badge npc-badge">NPC</span>
      </div>
      <div class="card-actions">
        <button v-if="editable" class="edit-btn" @click.stop="$emit('edit')" title="Редактировать">
          &#9998;
        </button>
        <button v-if="deletable" class="delete-btn" @click.stop="$emit('delete')" title="Удалить">
          &times;
        </button>
      </div>
    </div>

    <div class="card-info">
      <span v-if="character.class_name" class="class-name">{{ character.class_name }}</span>
      <span class="level">Ур. {{ character.level }}</span>
    </div>

    <div class="stats">
      <div class="stat" v-for="stat in stats" :key="stat.key">
        <span class="stat-label">{{ stat.label }}</span>
        <span class="stat-value">{{ (character as any)[stat.key] }}</span>
      </div>
    </div>

    <div class="bottom-row">
      <div class="hp-row">
        <span class="hp-label">HP</span>
        <span class="hp-value">{{ character.current_hp }} / {{ character.max_hp }}</span>
      </div>
      <div v-if="character.armor_class" class="ac-badge">
        <svg viewBox="0 0 40 46" class="ac-badge-svg">
          <path
            d="M20 2 L38 10 L38 24 C38 34 28 42 20 44 C12 42 2 34 2 24 L2 10 Z"
            fill="var(--color-bg-primary, #12121a)"
            stroke="var(--color-accent-primary, #c0a46c)"
            stroke-width="2.5"
          />
        </svg>
        <span class="ac-badge-value">{{ character.armor_class }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UserCharacter } from '@/types/models'

defineProps<{
  character: UserCharacter
  deletable?: boolean
  editable?: boolean
  selected?: boolean
  clickable?: boolean
}>()

defineEmits<{
  delete: []
  edit: []
  select: []
}>()

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
.character-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.character-card.clickable {
  cursor: pointer;
}

.character-card.clickable:hover {
  border-color: var(--color-primary);
}

.character-card.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.card-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.name {
  font-weight: 600;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.badge {
  font-size: var(--font-size-xs);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.npc-badge {
  background: var(--color-warning, #f59e0b);
  color: #000;
}

.card-actions {
  display: flex;
  gap: var(--spacing-1);
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.edit-btn:hover {
  color: var(--color-primary);
}

.delete-btn:hover {
  color: var(--color-danger, #ef4444);
}

.card-info {
  display: flex;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-1);
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-1);
  background: var(--color-bg-primary);
  border-radius: var(--radius-sm);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.stat-value {
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.bottom-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.hp-row {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-primary);
  border-radius: var(--radius-sm);
}

.hp-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-danger, #ef4444);
}

.hp-value {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.ac-badge {
  position: relative;
  width: 36px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ac-badge-svg {
  position: absolute;
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 1px 3px rgba(0, 0, 0, 0.4));
}

.ac-badge-value {
  position: relative;
  font-family: var(--font-family-display);
  font-size: 13px;
  font-weight: 700;
  color: var(--color-accent-primary, #c0a46c);
  line-height: 1;
  margin-top: -2px;
}
</style>
