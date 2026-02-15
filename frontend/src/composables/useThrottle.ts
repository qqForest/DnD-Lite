import { ref } from 'vue'

/**
 * Throttles function execution using requestAnimationFrame
 * Паттерн аналогичен useSwipe.ts (Pointer Events)
 */
export function useThrottle<T extends (...args: any[]) => void>(callback: T) {
  const rafId = ref<number | null>(null)
  let latestArgs: Parameters<T> | null = null

  function throttled(...args: Parameters<T>) {
    latestArgs = args
    if (rafId.value !== null) return

    rafId.value = requestAnimationFrame(() => {
      if (latestArgs) callback(...latestArgs)
      latestArgs = null
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
