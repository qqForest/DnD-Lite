import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GameMap, MapCreate, MapToken, MapTokenCreate, MapTokenUpdate } from '@/types/models'
import { mapsApi } from '@/services/api'
import { wsService } from '@/services/websocket'
import { useSessionStore } from './session'

export const useMapStore = defineStore('map', () => {
    const maps = ref<GameMap[]>([])
    const activeMapId = ref<string | null>(null)
    const loading = ref<boolean>(false)

    const activeMap = computed(() => {
        if (!activeMapId.value) return null
        return maps.value.find(m => m.id === activeMapId.value) || null
    })

    async function fetchSessionMaps() {
        const sessionStore = useSessionStore()
        if (!sessionStore.token) return

        loading.value = true
        try {
            maps.value = await mapsApi.list()
            // Find active map
            const active = maps.value.find(m => m.is_active)
            if (active) {
                activeMapId.value = active.id
            }
        } catch (error) {
            console.error('Failed to fetch maps:', error)
        } finally {
            loading.value = false
        }
    }

    async function createMap(data: MapCreate) {
        try {
            const newMap = await mapsApi.create(data)
            maps.value.push(newMap)
            return newMap
        } catch (error) {
            console.error('Failed to create map:', error)
            throw error
        }
    }

    async function setActiveMap(mapId: string) {
        try {
            await mapsApi.setActive(mapId)
            // Optimistic update
            maps.value.forEach(m => m.is_active = (m.id === mapId))
            activeMapId.value = mapId
        } catch (error) {
            console.error('Failed to set active map:', error)
            throw error
        }
    }

    async function addToken(mapId: string, data: MapTokenCreate) {
        try {
            const token = await mapsApi.addToken(mapId, data)
            const map = maps.value.find(m => m.id === mapId)
            if (map) {
                map.tokens.push(token)
            }
            return token
        } catch (error) {
            console.error('Failed to add token:', error)
            throw error
        }
    }

    // Throttled update handled by component usually, but this action sends immediately
    async function updateToken(tokenId: string, data: MapTokenUpdate) {
        try {
            // Optimistic local update not strictly necessary if we wait for WS, 
            // but for drag move we might want to skip this call and rely on WS?
            // Actually usually we send update and wait for ack or ignore. 
            // But here we just fire and forget for drag moves via WS? 
            // No, for persistence we call API. For smooth movement we might want WS.
            // Current design: Client calls API PATCH for persistence. 
            // API broadcasts WS. 
            // Creating a separate WS event for 'move' vs 'update' might be better for performance?
            // Plan said: "move_token: Client -> Server via WS" but we implemented REST PATCH.
            // Let's stick to REST PATCH for now. If performance is bad, we switch to pure WS for movement.

            const token = await mapsApi.updateToken(tokenId, data)
            // Update local state is handled by WS handler usually to avoid conflict?
            // But let's update locally too for responsiveness if not broadcasting back to sender.
            // Backend handles `exclude_token`. So we MUST update locally.

            const map = maps.value.find(m => m.tokens.some(t => t.id === tokenId))
            if (map) {
                const tIndex = map.tokens.findIndex(t => t.id === tokenId)
                if (tIndex > -1) {
                    // Merge updates
                    map.tokens[tIndex] = { ...map.tokens[tIndex], ...token }
                }
            }
            return token
        } catch (error) {
            console.error('Failed to update token:', error)
            throw error
        }
    }

    async function deleteToken(tokenId: string) {
        try {
            await mapsApi.deleteToken(tokenId)
            // Local update handled by WS or manually
            // WS will broadcast token_removed
        } catch (error) {
            console.error('Failed to delete token:', error)
            throw error
        }
    }

    // WebSocket Handlers
    const isHandlersSetup = ref(false)

    function setupWebSocketHandlers() {
        if (isHandlersSetup.value) return
        isHandlersSetup.value = true

        wsService.on('map_changed', (data: { map_id: string, name: string, background_url: string }) => {
            // If we have the map, update it. If not, maybe fetchall?
            const map = maps.value.find(m => m.id === data.map_id)
            if (map) {
                maps.value.forEach(m => m.is_active = (m.id === data.map_id))
                activeMapId.value = data.map_id
            } else {
                // New map or unknown, fetch all
                fetchSessionMaps()
            }
        })

        wsService.on('token_added', (data: { map_id: string, token: MapToken }) => {
            const map = maps.value.find(m => m.id === data.map_id)
            if (map) {
                // Check if exists
                if (!map.tokens.find(t => t.id === data.token.id)) {
                    map.tokens.push(data.token)
                }
            } else {
                // Map not loaded yet — fetch all maps to sync state
                fetchSessionMaps()
            }
        })

        wsService.on('token_updated', (data: { map_id: string, token_id: string, changes: Partial<MapToken> }) => {
            const map = maps.value.find(m => m.id === data.map_id)
            if (map) {
                const token = map.tokens.find(t => t.id === data.token_id)
                if (token) {
                    Object.assign(token, data.changes)
                }
            } else {
                fetchSessionMaps()
            }
        })

        wsService.on('token_removed', (data: { map_id: string, token_id: string }) => {
            const map = maps.value.find(m => m.id === data.map_id)
            if (map) {
                map.tokens = map.tokens.filter(t => t.id !== data.token_id)
            }
        })

        wsService.on('map_created', (data: { map: GameMap }) => {
            if (!maps.value.find(m => m.id === data.map.id)) {
                maps.value.push(data.map)
            }
        })
    }

    return {
        maps,
        activeMapId,
        activeMap,
        loading,
        fetchSessionMaps,
        createMap,
        setActiveMap,
        addToken,
        updateToken,
        deleteToken,
        setupWebSocketHandlers
    }
})
