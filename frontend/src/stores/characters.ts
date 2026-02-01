import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Character, CharacterCreate, CharacterUpdate, CreateFromTemplateRequest } from '@/types/models'
import { charactersApi, templatesApi } from '@/services/api'
import { wsService } from '@/services/websocket'
import { useSessionStore } from './session'

export const useCharactersStore = defineStore('characters', () => {
  const characters = ref<Character[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref<boolean>(false)

  const selected = computed(() => {
    return characters.value.find(c => c.id === selectedId.value) || null
  })

  const byPlayer = computed(() => {
    return (playerId: number) => characters.value.filter(c => c.player_id === playerId)
  })

  async function fetchAll() {
    const sessionStore = useSessionStore()
    if (!sessionStore.token) return

    loading.value = true
    try {
      characters.value = await charactersApi.list()
    } catch (error) {
      console.error('Failed to fetch characters:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(characterId: number) {
    const sessionStore = useSessionStore()
    if (!sessionStore.token) return

    try {
      const character = await charactersApi.get(characterId)
      const index = characters.value.findIndex(c => c.id === characterId)
      if (index > -1) {
        characters.value[index] = character
      } else {
        characters.value.push(character)
      }
      return character
    } catch (error) {
      console.error('Failed to fetch character:', error)
      throw error
    }
  }

  async function create(data: CharacterCreate) {
    const sessionStore = useSessionStore()
    if (!sessionStore.token) throw new Error('Not authenticated')

    try {
      const character = await charactersApi.create(data)
      characters.value.push(character)
      return character
    } catch (error) {
      console.error('Failed to create character:', error)
      throw error
    }
  }

  async function createFromTemplate(data: CreateFromTemplateRequest) {
    const sessionStore = useSessionStore()
    if (!sessionStore.token) throw new Error('Not authenticated')

    try {
      const character = await templatesApi.createCharacter(data)
      characters.value.push(character)
      return character
    } catch (error) {
      console.error('Failed to create character from template:', error)
      throw error
    }
  }

  async function update(characterId: number, data: CharacterUpdate) {
    const sessionStore = useSessionStore()
    if (!sessionStore.token) throw new Error('Not authenticated')

    try {
      const character = await charactersApi.update(characterId, data)
      const index = characters.value.findIndex(c => c.id === characterId)
      if (index > -1) {
        characters.value[index] = character
      }
      return character
    } catch (error) {
      console.error('Failed to update character:', error)
      throw error
    }
  }

  async function remove(characterId: number) {
    const sessionStore = useSessionStore()
    if (!sessionStore.token) throw new Error('Not authenticated')

    try {
      await charactersApi.delete(characterId)
      characters.value = characters.value.filter(c => c.id !== characterId)
      if (selectedId.value === characterId) {
        selectedId.value = null
      }
    } catch (error) {
      console.error('Failed to delete character:', error)
      throw error
    }
  }

  function select(characterId: number | null) {
    selectedId.value = characterId
  }

  const isHandlersSetup = ref(false)

  function setupWebSocketHandlers() {
    if (isHandlersSetup.value) return
    isHandlersSetup.value = true

    wsService.on('character_created', (data: { character: Character }) => {
      const existingIndex = characters.value.findIndex(c => c.id === data.character.id)
      if (existingIndex === -1) {
        characters.value.push(data.character)
      }
    })

    wsService.on('character_updated', (data: { character: Character }) => {
      const index = characters.value.findIndex(c => c.id === data.character.id)
      if (index > -1) {
        characters.value[index] = data.character
      }
    })

    wsService.on('character_deleted', (data: { character_id: number }) => {
      characters.value = characters.value.filter(c => c.id !== data.character_id)
      if (selectedId.value === data.character_id) {
        selectedId.value = null
      }
    })
  }

  return {
    characters,
    selectedId,
    loading,
    selected,
    byPlayer,
    fetchAll,
    fetchOne,
    create,
    createFromTemplate,
    update,
    remove,
    select,
    setupWebSocketHandlers
  }
})
