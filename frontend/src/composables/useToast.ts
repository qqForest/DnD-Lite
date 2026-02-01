export function useToast() {
  const toast = (window as any).__toast

  if (!toast) {
    // Fallback если Toast компонент еще не загружен
    return {
      success: (message: string) => console.log('Toast:', message),
      error: (message: string) => console.error('Toast:', message),
      info: (message: string) => console.info('Toast:', message)
    }
  }

  return {
    success: (message: string, duration?: number) => toast.success(message, duration),
    error: (message: string, duration?: number) => toast.error(message, duration),
    info: (message: string, duration?: number) => toast.info(message, duration)
  }
}
