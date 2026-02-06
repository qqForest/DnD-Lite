import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserMap, GameMap, MapToken, UserMapTokenCreate, UserMapTokenUpdate } from '@/types/models'
import { userMapsApi } from '@/services/api'

export const useMapEditorStore = defineStore('mapEditor', () => {
  const currentMap = ref<UserMap | null>(null)
  const loading = ref(false)

  /**
   * Transforms UserMap into the shape GameMap.vue expects,
   * mapping UserMapTokens to MapToken-like objects.
   */
  const activeMapForCanvas = computed<GameMap | null>(() => {
    if (!currentMap.value) return null
    const m = currentMap.value
    const tokens: MapToken[] = (m.tokens || []).map(t => ({
      id: t.id,
      map_id: t.user_map_id,
      character_id: null,
      type: t.type,
      x: t.x,
      y: t.y,
      scale: t.scale,
      rotation: t.rotation,
      layer: t.layer,
      label: t.label,
      color: t.color,
      icon: t.icon,
    }))
    return {
      id: m.id,
      session_id: 0,
      name: m.name,
      background_url: m.background_url,
      width: m.width,
      height: m.height,
      grid_scale: m.grid_scale,
      is_active: true,
      tokens,
    }
  })

  async function loadMap(id: string) {
    loading.value = true
    try {
      currentMap.value = await userMapsApi.get(id)
    } finally {
      loading.value = false
    }
  }

  async function addToken(data: UserMapTokenCreate) {
    if (!currentMap.value) return
    const token = await userMapsApi.addToken(currentMap.value.id, data)
    if (!currentMap.value.tokens) currentMap.value.tokens = []
    currentMap.value.tokens.push(token)
    return token
  }

  async function updateToken(tokenId: string, data: UserMapTokenUpdate) {
    const token = await userMapsApi.updateToken(tokenId, data)
    if (currentMap.value?.tokens) {
      const idx = currentMap.value.tokens.findIndex(t => t.id === tokenId)
      if (idx > -1) {
        currentMap.value.tokens[idx] = { ...currentMap.value.tokens[idx], ...token }
      }
    }
    return token
  }

  async function deleteToken(tokenId: string) {
    await userMapsApi.deleteToken(tokenId)
    if (currentMap.value?.tokens) {
      currentMap.value.tokens = currentMap.value.tokens.filter(t => t.id !== tokenId)
    }
  }

  return {
    currentMap,
    loading,
    activeMapForCanvas,
    loadMap,
    addToken,
    updateToken,
    deleteToken,
  }
})
