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
  InitiativeListResponse,
  GameMap,
  MapCreate,
  MapToken,
  MapTokenCreate,
  MapTokenUpdate,
  AuthResponse,
  User,
  UserCharacter,
  UserCharacterCreate,
  UserCharacterUpdate,
  UserMap,
  UserMapCreate,
  UserMapUpdate,
  UserMapToken,
  UserMapTokenCreate,
  UserMapTokenUpdate,
  UserStats
} from '@/types/models'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: Attach Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Refresh Logic
let isRefreshing = false
let failedQueue: Array<{ resolve: (v: unknown) => void; reject: (e: unknown) => void }> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Response Interceptor: Handle 401
api.interceptors.response.use(
  (response) => response,
  async (error: any) => {
    const originalRequest = error.config

    // Check if error is 401 and we haven't retried yet
    // Also ignore 401 on login/refresh endpoints to avoid loops (though login is 200 usually)
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/refresh')) {

      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = 'Bearer ' + token
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refreshToken')
      if (!refreshToken) {
        // No refresh token, logout
        logoutAndRedirect()
        return Promise.reject(error)
      }

      try {
        // Call refresh endpoint
        // Start a new axios instance to avoid interceptors? Or just use axios directly.
        // We need to send { access_token: "", refresh_token: ..., token_type: "bearer" }
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
        const url = `${baseUrl.replace(/\/$/, '')}/auth/refresh`

        const response = await axios.post(url, {
          access_token: "",
          refresh_token: refreshToken,
          token_type: "bearer"
        })

        const { access_token, refresh_token: newRefresh } = response.data

        localStorage.setItem('accessToken', access_token)
        localStorage.setItem('refreshToken', newRefresh)

        // Update headers
        api.defaults.headers.common['Authorization'] = 'Bearer ' + access_token
        originalRequest.headers.Authorization = 'Bearer ' + access_token

        processQueue(null, access_token)
        return api(originalRequest)
      } catch (err) {
        processQueue(err, null)
        logoutAndRedirect()
        return Promise.reject(err)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

function logoutAndRedirect() {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('userAccessToken')
  localStorage.removeItem('userRefreshToken')
  localStorage.removeItem('token')
  localStorage.removeItem('playerId')
  localStorage.removeItem('user')
  window.location.href = '/login'
}

// Session API
export const sessionApi = {
  createSession: async (data?: { user_map_id?: string }): Promise<SessionResponse> => {
    const response = await api.post<SessionResponse>('/session', data || {})
    return response.data
  },

  joinSession: async (data: SessionJoin): Promise<SessionJoinResponse> => {
    const response = await api.post<SessionJoinResponse>('/session/join', data)
    return response.data
  },

  getSessionState: async (): Promise<Session> => {
    const response = await api.get<Session>('/session')
    return response.data
  },

  getPlayers: async (): Promise<Player[]> => {
    const response = await api.get<Player[]>('/session/players')
    return response.data
  },

  startSession: async (): Promise<{ message: string; session_started: boolean }> => {
    const response = await api.post<{ message: string; session_started: boolean }>('/session/start')
    return response.data
  },

  setReady: async (isReady: boolean): Promise<{ message: string; is_ready: boolean }> => {
    const response = await api.post<{ message: string; is_ready: boolean }>('/session/ready', { is_ready: isReady })
    return response.data
  },

  toggleMovement: async (playerId: number): Promise<{ player_id: number; can_move: boolean }> => {
    const response = await api.patch<{ player_id: number; can_move: boolean }>(`/players/${playerId}/movement`)
    return response.data
  },

  deleteSession: async (): Promise<{ message: string; session_code: string }> => {
    const response = await api.delete<{ message: string; session_code: string }>('/session')
    return response.data
  }
}

// Characters API
export const charactersApi = {
  list: async (): Promise<Character[]> => {
    const response = await api.get<Character[]>('/characters')
    return response.data
  },

  get: async (characterId: number): Promise<Character> => {
    const response = await api.get<Character>(`/characters/${characterId}`)
    return response.data
  },

  create: async (data: CharacterCreate): Promise<Character> => {
    const response = await api.post<Character>('/characters', data)
    return response.data
  },

  update: async (characterId: number, data: CharacterUpdate): Promise<Character> => {
    const response = await api.patch<Character>(`/characters/${characterId}`, data)
    return response.data
  },

  delete: async (characterId: number): Promise<void> => {
    await api.delete(`/characters/${characterId}`)
  },

  generateAvatar: async (characterId: number): Promise<Character> => {
    const response = await api.post<Character>(`/characters/${characterId}/generate-avatar`)
    return response.data
  }
}

// Dice API
export const diceApi = {
  roll: async (data: DiceRoll): Promise<DiceResult> => {
    const response = await api.post<DiceResult>('/dice/roll', data)
    return response.data
  }
}

// Combat API
export const combatApi = {
  getState: async (): Promise<Combat | { active: false }> => {
    const response = await api.get<Combat | { active: false }>('/combat')
    return response.data
  },

  start: async (characterIds: number[]): Promise<Combat> => {
    // characterIds is optional body or params? Old code used query params.
    // Updated backend still supports character_ids as query param?
    // Backend: async def start_combat(character_ids: Optional[List[int]] = None, ...)
    // It's a query param mostly, or body if json. FastAPI differentiates by default. If list, usually query.
    // Let's pass as query params manually.
    const params = new URLSearchParams()
    characterIds.forEach(id => params.append('character_ids', id.toString()))
    const response = await api.post<Combat>(`/combat/start?${params.toString()}`)
    return response.data
  },

  end: async (): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/combat/end')
    return response.data
  },

  nextTurn: async (): Promise<{ participant_id: number; character_id: number; round_number: number }> => {
    const response = await api.post('/combat/next-turn')
    return response.data
  },

  rollInitiative: async (): Promise<InitiativeRollResponse> => {
    const response = await api.post<InitiativeRollResponse>('/combat/initiative')
    return response.data
  },

  getInitiativeList: async (): Promise<InitiativeListResponse> => {
    const response = await api.get<InitiativeListResponse>('/combat/initiative')
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

  createCharacter: async (data: CreateFromTemplateRequest): Promise<Character> => {
    const response = await api.post<Character>('/templates/create', data)
    return response.data
  }
}

// Persistence API
export const persistenceApi = {
  exportSession: async (includeCombat: boolean = true): Promise<any> => {
    const response = await api.post('/session/export', { include_combat: includeCombat })
    return response.data
  },

  exportSessionDownload: async (includeCombat: boolean = true): Promise<Blob> => {
    // For blob download, we must use axios with responseType blob.
    // Interceptor will attach token.
    const response = await api.post('/session/export/download', { include_combat: includeCombat }, {
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

// Maps API
export const mapsApi = {
  list: async (): Promise<GameMap[]> => {
    const response = await api.get<GameMap[]>('/session/maps')
    return response.data
  },

  get: async (mapId: string): Promise<GameMap> => {
    const response = await api.get<GameMap>(`/maps/${mapId}`)
    return response.data
  },

  create: async (data: MapCreate): Promise<GameMap> => {
    const response = await api.post<GameMap>('/session/maps', data)
    return response.data
  },

  setActive: async (mapId: string): Promise<GameMap> => {
    const response = await api.put<GameMap>(`/maps/${mapId}/active`)
    return response.data
  },

  addToken: async (mapId: string, data: MapTokenCreate): Promise<MapToken> => {
    const response = await api.post<MapToken>(`/maps/${mapId}/tokens`, data)
    return response.data
  },

  updateToken: async (tokenId: string, data: MapTokenUpdate): Promise<MapToken> => {
    const response = await api.patch<MapToken>(`/tokens/${tokenId}`, data)
    return response.data
  },

  deleteToken: async (tokenId: string): Promise<void> => {
    await api.delete(`/tokens/${tokenId}`)
  },

  saveToLibrary: async (mapId: string): Promise<{ message: string; user_map_id: string }> => {
    const response = await api.post<{ message: string; user_map_id: string }>(`/maps/${mapId}/save-to-library`)
    return response.data
  }
}

// Auth API
export const authApi = {
  register: async (data: { username: string; display_name: string; password: string; role: string }): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/users/register', data)
    return response.data
  },

  login: async (data: { username: string; password: string }): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/users/login', data)
    return response.data
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  getStats: async (): Promise<UserStats> => {
    const response = await api.get<UserStats>('/users/me/stats')
    return response.data
  }
}

// User Characters API
export const userCharactersApi = {
  list: async (isNpc?: boolean): Promise<UserCharacter[]> => {
    const params = isNpc !== undefined ? { is_npc: isNpc } : {}
    const response = await api.get<UserCharacter[]>('/me/characters', { params })
    return response.data
  },

  get: async (id: number): Promise<UserCharacter> => {
    const response = await api.get<UserCharacter>(`/me/characters/${id}`)
    return response.data
  },

  create: async (data: UserCharacterCreate): Promise<UserCharacter> => {
    const response = await api.post<UserCharacter>('/me/characters', data)
    return response.data
  },

  update: async (id: number, data: UserCharacterUpdate): Promise<UserCharacter> => {
    const response = await api.patch<UserCharacter>(`/me/characters/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/me/characters/${id}`)
  },

  generateAvatar: async (id: number): Promise<UserCharacter> => {
    const response = await api.post<UserCharacter>(`/me/characters/${id}/generate-avatar`)
    return response.data
  }
}

// User Maps API
export const userMapsApi = {
  list: async (): Promise<UserMap[]> => {
    const response = await api.get<UserMap[]>('/me/maps')
    return response.data
  },

  get: async (id: string): Promise<UserMap> => {
    const response = await api.get<UserMap>(`/me/maps/${id}`)
    return response.data
  },

  create: async (data: UserMapCreate): Promise<UserMap> => {
    const response = await api.post<UserMap>('/me/maps', data)
    return response.data
  },

  update: async (id: string, data: UserMapUpdate): Promise<UserMap> => {
    const response = await api.patch<UserMap>(`/me/maps/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/me/maps/${id}`)
  },

  uploadBackground: async (file: File): Promise<{ url: string; width: number; height: number }> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<{ url: string; width: number; height: number }>(
      '/me/maps/upload-background',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return response.data
  },

  addToken: async (mapId: string, data: UserMapTokenCreate): Promise<UserMapToken> => {
    const response = await api.post<UserMapToken>(`/me/maps/${mapId}/tokens`, data)
    return response.data
  },

  updateToken: async (tokenId: string, data: UserMapTokenUpdate): Promise<UserMapToken> => {
    const response = await api.patch<UserMapToken>(`/me/maps/tokens/${tokenId}`, data)
    return response.data
  },

  deleteToken: async (tokenId: string): Promise<void> => {
    await api.delete(`/me/maps/tokens/${tokenId}`)
  }
}

export { api }
export default api
