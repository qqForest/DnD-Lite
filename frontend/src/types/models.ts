export interface Session {
  id: number
  code: string
  is_active: boolean
  session_started: boolean
  created_at: string
  player_count: number
}

export interface SessionResponse {
  code: string
  gm_token: string
}

export interface SessionJoin {
  code: string
  name: string
}

export interface SessionJoinResponse {
  player_id: number
  token: string
  session_code: string
}

export interface Player {
  id: number
  name: string
  is_gm: boolean
  is_online?: boolean
  is_ready?: boolean
}

export interface Character {
  id: number
  player_id: number
  name: string
  class_name: string | null
  level: number
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
  max_hp: number
  current_hp: number
}

export interface CharacterCreate {
  name: string
  class_name?: string | null
  level?: number
  strength?: number
  dexterity?: number
  constitution?: number
  intelligence?: number
  wisdom?: number
  charisma?: number
  max_hp?: number
  current_hp?: number | null
}

export interface CharacterUpdate {
  name?: string
  class_name?: string | null
  level?: number
  strength?: number
  dexterity?: number
  constitution?: number
  intelligence?: number
  wisdom?: number
  charisma?: number
  max_hp?: number
  current_hp?: number | null
}

export interface DiceRoll {
  dice: string
  reason?: string | null
}

export interface DiceResult {
  dice: string
  rolls: number[]
  modifier: number
  total: number
  formula: string
  reason: string | null
  player_name: string
  timestamp?: string
}

export interface CombatParticipant {
  id: number
  character_id: number
  character_name: string
  initiative: number
  current_hp: number
  is_active: boolean
}

export interface InitiativeEntry {
  player_id: number
  player_name: string
  character_name: string | null
  roll: number | null
  is_npc: boolean
}

export interface InitiativeListResponse {
  entries: InitiativeEntry[]
}

export interface InitiativeRollResponse {
  roll: number
  player_name: string
}

export interface Combat {
  id: number
  is_active: boolean
  round_number: number
  current_turn_id: number | null
  participants: CombatParticipant[]
  initiative_list?: InitiativeEntry[]
}

export interface StartingItemSchema {
  name: string
  description?: string | null
  effects?: Record<string, any> | null
  is_equipped: boolean
}

export interface StartingSpellSchema {
  name: string
  level: number
  description?: string | null
  damage_dice?: string | null
}

export interface ClassTemplateListItem {
  id: string
  name: string
  name_ru: string
  description_ru: string
  hit_die: string
  primary_abilities: string[]
}

export interface ClassTemplateResponse {
  id: string
  name: string
  name_ru: string
  description: string
  description_ru: string
  hit_die: string
  primary_abilities: string[]
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
  recommended_hp: number
  starting_items: StartingItemSchema[]
  starting_spells: StartingSpellSchema[]
}

export interface CreateFromTemplateRequest {
  template_id: string
  name: string
  level?: number
  include_items?: boolean
  include_spells?: boolean
}
