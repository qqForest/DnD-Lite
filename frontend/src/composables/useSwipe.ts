import { ref } from 'vue'

export function useSwipe(options?: { threshold?: number }) {
  const threshold = options?.threshold ?? 50

  const offsetX = ref(0)
  const isSwiping = ref(false)

  let startX = 0
  let startY = 0
  let directionLocked: 'horizontal' | 'vertical' | null = null
  let pointerId: number | null = null

  let onSwipeLeft: (() => void) | null = null
  let onSwipeRight: (() => void) | null = null

  function onPointerDown(e: PointerEvent) {
    startX = e.clientX
    startY = e.clientY
    offsetX.value = 0
    directionLocked = null
    pointerId = e.pointerId
    // НЕ захватываем pointer сразу, дождёмся движения
  }

  function onPointerMove(e: PointerEvent) {
    if (pointerId === null || e.pointerId !== pointerId) return

    const dx = e.clientX - startX
    const dy = e.clientY - startY

    if (!directionLocked) {
      const absDx = Math.abs(dx)
      const absDy = Math.abs(dy)
      if (absDx < 10 && absDy < 10) return
      directionLocked = absDx > absDy ? 'horizontal' : 'vertical'

      // Захватываем pointer только когда начался реальный свайп
      if (directionLocked === 'horizontal') {
        ;(e.currentTarget as HTMLElement)?.setPointerCapture(e.pointerId)
      }
    }

    if (directionLocked === 'horizontal') {
      e.preventDefault()
      offsetX.value = dx
      isSwiping.value = true
    }
  }

  function onPointerUp(e: PointerEvent) {
    if (pointerId === null || e.pointerId !== pointerId) return

    if (directionLocked === 'horizontal') {
      if (offsetX.value <= -threshold && onSwipeLeft) {
        onSwipeLeft()
      } else if (offsetX.value >= threshold && onSwipeRight) {
        onSwipeRight()
      }

      // Освобождаем pointer если захватывали
      try {
        ;(e.currentTarget as HTMLElement)?.releasePointerCapture(e.pointerId)
      } catch {
        // Игнорируем ошибки если capture не был установлен
      }
    }

    offsetX.value = 0
    isSwiping.value = false
    pointerId = null
    directionLocked = null
  }

  function onPointerCancel(e: PointerEvent) {
    if (pointerId !== null && e.pointerId === pointerId) {
      try {
        ;(e.currentTarget as HTMLElement)?.releasePointerCapture(e.pointerId)
      } catch {
        // Игнорируем ошибки
      }
    }

    offsetX.value = 0
    isSwiping.value = false
    pointerId = null
    directionLocked = null
  }

  const handlers = {
    onPointerdown: onPointerDown,
    onPointermove: onPointerMove,
    onPointerup: onPointerUp,
    onPointercancel: onPointerCancel,
  }

  return {
    offsetX,
    isSwiping,
    handlers,
    onSwipeLeft: (fn: () => void) => { onSwipeLeft = fn },
    onSwipeRight: (fn: () => void) => { onSwipeRight = fn },
  }
}
