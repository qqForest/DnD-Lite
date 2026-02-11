import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { combatApi } from '@/services/api'
import { wsService } from '@/services/websocket'

export interface InitiativeEntry {
    player_id: number
    player_name: string
    character_id?: number | null
    character_name: string | null
    roll: number | null
    is_npc: boolean
}

export const useCombatStore = defineStore('combat', () => {
    const isActive = ref(false)
    const combatId = ref<number | null>(null)
    const initiativeList = ref<InitiativeEntry[]>([])
    const showInitiativeModal = ref(false)
    const myInitiativeRoll = ref<number | null>(null)
    const isRolling = ref(false)

    const hasRolled = computed(() => myInitiativeRoll.value !== null)

    async function startCombat() {
        const response = await combatApi.start([])
        isActive.value = true
        combatId.value = response.id
        initiativeList.value = []
    }

    async function endCombat() {
        await combatApi.end()
        resetState()
    }

    async function rollInitiative(): Promise<number> {
        if (isRolling.value || hasRolled.value) {
            throw new Error('Already rolling or rolled')
        }

        isRolling.value = true
        try {
            const response = await combatApi.rollInitiative()
            myInitiativeRoll.value = response.roll
            return response.roll
        } finally {
            isRolling.value = false
        }
    }

    async function rollInitiativeForNpc(characterId: number): Promise<number> {
        try {
            console.log('[Combat Store] Calling API to roll initiative for NPC:', characterId)
            const response = await combatApi.rollInitiativeForNpc(characterId)
            console.log('[Combat Store] API response:', response)
            return response.roll
        } catch (error) {
            console.error('[Combat Store] Failed to roll initiative for NPC:', error)
            throw error
        }
    }

    async function fetchInitiativeList() {
        const response = await combatApi.getInitiativeList()
        initiativeList.value = response.entries
    }

    async function fetchCombatState() {
        const response = await combatApi.getState()
        if ('active' in response && response.active === false) {
            isActive.value = false
            combatId.value = null
            initiativeList.value = []
        } else if ('id' in response) {
            isActive.value = response.is_active
            combatId.value = response.id
            if (response.initiative_list) {
                initiativeList.value = response.initiative_list
            }
        }
    }

    function resetState() {
        isActive.value = false
        combatId.value = null
        initiativeList.value = []
        showInitiativeModal.value = false
        myInitiativeRoll.value = null
        isRolling.value = false
    }

    function setupWebSocketHandlers() {
        wsService.on('combat_started', (data: { combat_id: number }) => {
            isActive.value = true
            combatId.value = data.combat_id
            initiativeList.value = []
            myInitiativeRoll.value = null
            showInitiativeModal.value = true
        })

        wsService.on('combat_ended', () => {
            resetState()
        })

        wsService.on('initiative_rolled', (data: {
            player_id?: number
            character_id?: number
            player_name: string
            character_name?: string
            roll: number
            is_npc?: boolean
        }) => {
            console.log('[Combat Store] initiative_rolled event received:', data)

            // Handle NPC roll
            if (data.is_npc && data.character_id) {
                console.log('[Combat Store] Processing NPC initiative roll:', data)
                const existingIndex = initiativeList.value.findIndex(
                    e => e.character_id === data.character_id && e.is_npc
                )
                if (existingIndex !== -1) {
                    initiativeList.value[existingIndex].roll = data.roll
                } else {
                    initiativeList.value.push({
                        player_id: 0, // Sentinel value for NPCs
                        player_name: 'NPC',
                        character_id: data.character_id,
                        character_name: data.character_name || 'Неизвестный NPC',
                        roll: data.roll,
                        is_npc: true
                    })
                }
            }
            // Handle player roll
            else if (data.player_id) {
                const existingIndex = initiativeList.value.findIndex(e => e.player_id === data.player_id)
                if (existingIndex !== -1) {
                    initiativeList.value[existingIndex].roll = data.roll
                } else {
                    initiativeList.value.push({
                        player_id: data.player_id,
                        player_name: data.player_name,
                        character_name: data.character_name || null,
                        roll: data.roll,
                        is_npc: false
                    })
                }
            }

            // Re-sort list
            initiativeList.value.sort((a, b) => {
                if (a.roll === null && b.roll === null) return 0
                if (a.roll === null) return 1
                if (b.roll === null) return -1
                return b.roll - a.roll
            })
        })
    }

    function closeInitiativeModal() {
        showInitiativeModal.value = false
    }

    return {
        isActive,
        combatId,
        initiativeList,
        showInitiativeModal,
        myInitiativeRoll,
        isRolling,
        hasRolled,
        startCombat,
        endCombat,
        rollInitiative,
        rollInitiativeForNpc,
        fetchInitiativeList,
        fetchCombatState,
        resetState,
        setupWebSocketHandlers,
        closeInitiativeModal
    }
})
