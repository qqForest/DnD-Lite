import { ref } from 'vue'

/**
 * Throttles function execution using requestAnimationFrame
 * Паттерн аналогичен useSwipe.ts (Pointer Events)
 */
export function useThrottle<T extends (...args: any[]) => void>(callback: T) {
  const rafId = ref<number | null>(null)

  function throttled(...args: Parameters<T>) {
    if (rafId.value !== null) return

    rafId.value = requestAnimationFrame(() => {
      callback(...args)
      rafId.value = null
    })
  }

  function cancel() {
    if (rafId.value !== null) {
      cancelAnimationFrame(rafId.value)
      rafId.value = null
    }
  }

  return { throttled, cancel }
}
