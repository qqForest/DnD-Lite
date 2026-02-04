import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserCharacter, UserMap } from '@/types/models'
import { userCharactersApi, userMapsApi } from '@/services/api'

export const useProfileStore = defineStore('profile', () => {
  const characters = ref<UserCharacter[]>([])
  const maps = ref<UserMap[]>([])
  const loading = ref(false)

  const playerCharacters = computed(() => characters.value.filter(c => !c.is_npc))
  const npcCharacters = computed(() => characters.value.filter(c => c.is_npc))

  async function fetchCharacters() {
    loading.value = true
    try {
      characters.value = await userCharactersApi.list()
    } catch (error) {
      console.error('Failed to fetch user characters:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchMaps() {
    loading.value = true
    try {
      maps.value = await userMapsApi.list()
    } catch (error) {
      console.error('Failed to fetch user maps:', error)
    } finally {
      loading.value = false
    }
  }

  async function deleteCharacter(id: number) {
    await userCharactersApi.delete(id)
    characters.value = characters.value.filter(c => c.id !== id)
  }

  async function deleteMap(id: string) {
    await userMapsApi.delete(id)
    maps.value = maps.value.filter(m => m.id !== id)
  }

  return {
    characters,
    maps,
    loading,
    playerCharacters,
    npcCharacters,
    fetchCharacters,
    fetchMaps,
    deleteCharacter,
    deleteMap,
  }
})
