<template>
  <div class="carousel-wrapper">
    <div
      v-if="templates.length > 0"
      class="carousel"
      v-bind="handlers"
      style="touch-action: pan-y"
    >
      <div
        class="carousel-track"
        :style="trackStyle"
      >
        <div
          v-for="(tmpl, i) in templates"
          :key="tmpl.id"
          class="carousel-slide"
        >
          <ClassCard
            :template="tmpl"
            :details="i === currentIndex ? currentDetails : undefined"
          />
        </div>
      </div>
    </div>

    <p v-else class="empty-text">Шаблоны не найдены</p>

    <!-- Dots -->
    <div v-if="templates.length > 1" class="dots">
      <button
        v-for="(_, i) in templates"
        :key="i"
        class="dot-btn"
        :class="{ active: i === currentIndex }"
        @click="goTo(i)"
      >
        <span class="dot"></span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useSwipe } from '@/composables/useSwipe'
import ClassCard from './ClassCard.vue'
import type { ClassTemplateListItem, ClassTemplateResponse } from '@/types/models'

const props = defineProps<{
  templates: ClassTemplateListItem[]
  currentDetails?: ClassTemplateResponse
}>()

const currentIndex = ref(0)

defineExpose({ currentIndex })

const { offsetX, isSwiping, handlers, onSwipeLeft, onSwipeRight } = useSwipe({ threshold: 50 })

onSwipeLeft(() => {
  if (currentIndex.value < props.templates.length - 1) {
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
  const dragPercent = props.templates.length > 0
    ? (offsetX.value / window.innerWidth) * 100
    : 0
  return {
    transform: `translateX(${base + dragPercent}%)`,
    transition: isSwiping.value ? 'none' : 'transform 300ms ease-out',
  }
})

function goTo(index: number) {
  currentIndex.value = index
}

watch(() => props.templates.length, (len) => {
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
  flex-wrap: wrap;
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
