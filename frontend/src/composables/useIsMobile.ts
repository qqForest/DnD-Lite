import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Reactive composable для определения мобильных устройств
 * Критерии:
 * 1. Наличие touch поддержки ('ontouchstart' in window)
 * 2. Ширина экрана < 1024px (breakpoint-lg из tokens.css)
 *
 * Обновляется при resize для поддержки rotation
 */
export function useIsMobile() {
  const isMobile = ref(false)

  function checkIsMobile() {
    const hasTouch = 'ontouchstart' in window
    const isNarrowScreen = window.innerWidth < 1024
    isMobile.value = hasTouch && isNarrowScreen
  }

  onMounted(() => {
    checkIsMobile()
    window.addEventListener('resize', checkIsMobile)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', checkIsMobile)
  })

  return { isMobile }
}
