import axios, { AxiosInstance, AxiosError } from 'axios'
import type { ApiErrorResponse } from '@/types/api'
import type {
  SessionResponse,
  SessionJoin,
  SessionJoinResponse,
  Session,
  Player,
  Character,
  CharacterCreate,
  CharacterUpdate,
  DiceRoll,
  DiceResult,
  Combat,
  ClassTemplateListItem,
  ClassTemplateResponse,
  CreateFromTemplateRequest,
  InitiativeRollResponse,
  InitiativeListResponse
} from '@/types/models'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token && config.params) {
    config.params.token = token
  } else if (token) {
    config.params = { token }
  }
  return config
})

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// Session API
export const sessionApi = {
  createSession: async (): Promise<SessionResponse> => {
    const response = await api.post<SessionResponse>('/session')
    return response.data
  },

  joinSession: async (data: SessionJoin): Promise<SessionJoinResponse> => {
    const response = await api.post<SessionJoinResponse>('/session/join', data)
    return response.data
  },

  getSessionState: async (token: string): Promise<Session> => {
    const response = await api.get<Session>('/session', { params: { token } })
    return response.data
  },

  getPlayers: async (token: string): Promise<Player[]> => {
    const response = await api.get<Player[]>('/session/players', { params: { token } })
    return response.data
  },

  startSession: async (token: string): Promise<{ message: string; session_started: boolean }> => {
    const response = await api.post<{ message: string; session_started: boolean }>('/session/start', null, { params: { token } })
    return response.data
  },

  setReady: async (isReady: boolean, token: string): Promise<{ message: string; is_ready: boolean }> => {
    const response = await api.post<{ message: string; is_ready: boolean }>('/session/ready', { is_ready: isReady }, { params: { token } })
    return response.data
  }
}

// Characters API
export const charactersApi = {
  list: async (token: string): Promise<Character[]> => {
    const response = await api.get<Character[]>('/characters', { params: { token } })
    return response.data
  },

  get: async (characterId: number, token: string): Promise<Character> => {
    const response = await api.get<Character>(`/characters/${characterId}`, { params: { token } })
    return response.data
  },

  create: async (data: CharacterCreate, token: string): Promise<Character> => {
    const response = await api.post<Character>('/characters', data, { params: { token } })
    return response.data
  },

  update: async (characterId: number, data: CharacterUpdate, token: string): Promise<Character> => {
    const response = await api.patch<Character>(`/characters/${characterId}`, data, { params: { token } })
    return response.data
  },

  delete: async (characterId: number, token: string): Promise<void> => {
    await api.delete(`/characters/${characterId}`, { params: { token } })
  }
}

// Dice API
export const diceApi = {
  roll: async (data: DiceRoll, token: string): Promise<DiceResult> => {
    const response = await api.post<DiceResult>('/dice/roll', data, { params: { token } })
    return response.data
  }
}

// Combat API
export const combatApi = {
  getState: async (token: string): Promise<Combat | { active: false }> => {
    const response = await api.get<Combat | { active: false }>('/combat', { params: { token } })
    return response.data
  },

  start: async (characterIds: number[], token: string): Promise<Combat> => {
    const params = new URLSearchParams()
    characterIds.forEach(id => params.append('character_ids', id.toString()))
    params.append('token', token)
    const response = await api.post<Combat>(`/combat/start?${params.toString()}`)
    return response.data
  },

  end: async (token: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/combat/end', null, { params: { token } })
    return response.data
  },

  nextTurn: async (token: string): Promise<{ participant_id: number; character_id: number; round_number: number }> => {
    const response = await api.post('/combat/next-turn', null, { params: { token } })
    return response.data
  },

  rollInitiative: async (token: string): Promise<InitiativeRollResponse> => {
    const response = await api.post<InitiativeRollResponse>('/combat/initiative', null, { params: { token } })
    return response.data
  },

  getInitiativeList: async (token: string): Promise<InitiativeListResponse> => {
    const response = await api.get<InitiativeListResponse>('/combat/initiative', { params: { token } })
    return response.data
  }
}

// Templates API
export const templatesApi = {
  list: async (): Promise<ClassTemplateListItem[]> => {
    const response = await api.get<ClassTemplateListItem[]>('/templates')
    return response.data
  },

  get: async (templateId: string): Promise<ClassTemplateResponse> => {
    const response = await api.get<ClassTemplateResponse>(`/templates/${templateId}`)
    return response.data
  },

  createCharacter: async (data: CreateFromTemplateRequest, token: string): Promise<Character> => {
    const response = await api.post<Character>('/templates/create', data, { params: { token } })
    return response.data
  }
}

// Persistence API
export const persistenceApi = {
  exportSession: async (token: string, includeCombat: boolean = true): Promise<any> => {
    const response = await api.post('/session/export', { include_combat: includeCombat }, { params: { token } })
    return response.data
  },

  exportSessionDownload: async (token: string, includeCombat: boolean = true): Promise<Blob> => {
    const response = await api.post('/session/export/download', { include_combat: includeCombat }, {
      params: { token },
      responseType: 'blob'
    })
    return response.data
  },

  importSession: async (data: any, newSessionCode?: string): Promise<any> => {
    const response = await api.post('/session/import', {
      data,
      new_session_code: newSessionCode
    })
    return response.data
  },

  validateImport: async (data: any): Promise<any> => {
    const response = await api.post('/session/validate', { data })
    return response.data
  }
}

export { api }
export default api
