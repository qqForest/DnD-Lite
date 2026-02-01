import type { Player, Character, DiceResult, Combat } from './models'

export interface WebSocketMessage {
  event: string
  data: any
}

export interface PlayerJoinedEvent {
  player_id: number
  player_name: string
  is_gm: boolean
}

export interface PlayerLeftEvent {
  player_id: number
}

export interface CharacterCreatedEvent {
  character: Character
}

export interface CharacterUpdatedEvent {
  character: Character
}

export interface CharacterDeletedEvent {
  character_id: number
}

export interface DiceResultEvent {
  dice: string
  rolls: number[]
  modifier: number
  total: number
  reason: string | null
  player_name: string
}

export interface CombatStartedEvent {
  id: number
  is_active: boolean
  round_number: number
  current_turn_id: number | null
  participants: Array<{
    id: number
    character_id: number
    character_name: string
    initiative: number
    current_hp: number
    is_active: boolean
  }>
}

export interface CombatEndedEvent {
  // Empty for now
}

export interface TurnChangedEvent {
  participant_id: number
  character_id: number
  character_name: string
  round_number: number
}

export interface HPChangedEvent {
  character_id: number
  hp: number
  damage?: number
  heal?: number
}

export type WebSocketEvent =
  | { type: 'player_joined'; payload: PlayerJoinedEvent }
  | { type: 'player_left'; payload: PlayerLeftEvent }
  | { type: 'character_created'; payload: CharacterCreatedEvent }
  | { type: 'character_updated'; payload: CharacterUpdatedEvent }
  | { type: 'character_deleted'; payload: CharacterDeletedEvent }
  | { type: 'dice_result'; payload: DiceResultEvent }
  | { type: 'combat_started'; payload: CombatStartedEvent }
  | { type: 'combat_ended'; payload: CombatEndedEvent }
  | { type: 'turn_changed'; payload: TurnChangedEvent }
  | { type: 'hp_changed'; payload: HPChangedEvent }
