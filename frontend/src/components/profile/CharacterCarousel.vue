<template>
  <div class="carousel-wrapper">
    <div
      v-if="characters.length > 0"
      class="carousel"
      v-bind="handlers"
      style="touch-action: pan-y"
    >
      <div
        class="carousel-track"
        :style="trackStyle"
      >
        <div
          v-for="char in characters"
          :key="char.id"
          class="carousel-slide"
        >
          <CharacterFlipCard
            :character="char"
            :deletable="!readonly"
            :editable="!readonly"
            @delete="$emit('delete', char.id)"
            @edit="$emit('edit', char.id)"
          />
        </div>
      </div>
    </div>

    <p v-else class="empty-text">У вас пока нет персонажей</p>

    <!-- Dots -->
    <div v-if="characters.length > 1" class="dots">
      <button
        v-for="(_, i) in characters"
        :key="i"
        class="dot-btn"
        :class="{ active: i === currentIndex }"
        @click="currentIndex = i"
      >
        <span class="dot"></span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useSwipe } from '@/composables/useSwipe'
import CharacterFlipCard from './CharacterFlipCard.vue'
import type { UserCharacter } from '@/types/models'

const props = defineProps<{
  characters: UserCharacter[]
  readonly?: boolean
}>()

defineEmits<{
  delete: [id: number]
  edit: [id: number]
}>()

const currentIndex = ref(0)

defineExpose({ currentIndex })

const { offsetX, isSwiping, handlers, onSwipeLeft, onSwipeRight } = useSwipe({ threshold: 50 })

onSwipeLeft(() => {
  if (currentIndex.value < props.characters.length - 1) {
    currentIndex.value++
  }
})

onSwipeRight(() => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
})

const trackStyle = computed(() => {
  const base = -(currentIndex.value * 100)
  const dragPercent = props.characters.length > 0
    ? (offsetX.value / window.innerWidth) * 100
    : 0
  return {
    transform: `translateX(${base + dragPercent}%)`,
    transition: isSwiping.value ? 'none' : 'transform 300ms ease-out',
  }
})

watch(() => props.characters.length, (len) => {
  if (currentIndex.value >= len) {
    currentIndex.value = Math.max(0, len - 1)
  }
})
</script>

<style scoped>
.carousel-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
}

.carousel {
  width: 100%;
  overflow: hidden;
}

.carousel-track {
  display: flex;
}

.carousel-slide {
  flex: 0 0 100%;
  display: flex;
  justify-content: center;
  padding: 0 var(--spacing-4);
  box-sizing: border-box;
}

.empty-text {
  text-align: center;
  color: var(--color-text-secondary);
  padding: var(--spacing-8) 0;
  font-size: var(--font-size-base);
}

.dots {
  display: flex;
  gap: var(--spacing-1);
  justify-content: center;
}

.dot-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2);
  min-width: 44px;
  min-height: 44px;
  background: none;
  border: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted, var(--color-text-secondary));
  opacity: 0.4;
  transition: all 200ms ease;
}

.dot-btn.active .dot {
  opacity: 1;
  background: var(--color-accent-primary);
  box-shadow: var(--glow-accent);
}
</style>
