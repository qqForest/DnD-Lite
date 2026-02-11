<template>
  <v-group
    :config="{
      x: token.x,
      y: token.y,
      draggable: !isReadOnly,
      id: token.id,
      name: 'draggable-token'
    }"
    @dragstart="onDragStart"
    @dragend="onDragEnd"
    @dragmove="onDragMove"
    @click="onClick"
    @contextmenu="onContextMenu"
  >
    <!-- Selection Halo -->
    <v-circle
      v-if="selected"
      :config="{
        radius: (30 * token.scale) + 2,
        stroke: '#00aaff',
        strokeWidth: 2
      }"
    />

    <!-- Own token indicator (movable by player) -->
    <v-circle
      v-if="isOwnMovable && !selected"
      :config="{
        radius: (30 * token.scale) + 2,
        stroke: '#4AD94A',
        strokeWidth: 2,
        opacity: 0.8
      }"
    />

    <!-- Token Body: avatar image or colored circle -->
    <v-group v-if="avatarImage" :config="{ clipFunc: clipCircle }">
      <v-image
        :config="{
          image: avatarImage,
          x: -30 * token.scale,
          y: -30 * token.scale,
          width: 60 * token.scale,
          height: 60 * token.scale,
        }"
      />
    </v-group>
    <v-circle
      v-else
      :config="{
        radius: 30 * token.scale,
        fill: token.color || '#cccccc',
        stroke: 'black',
        strokeWidth: 1,
        shadowBlur: 5
      }"
    />

    <!-- Border ring (over avatar or colored circle) -->
    <v-circle
      :config="{
        radius: 30 * token.scale,
        stroke: avatarImage ? '#333' : 'black',
        strokeWidth: avatarImage ? 2 : 1,
        shadowBlur: avatarImage ? 0 : 5,
      }"
    />

    <!-- Icon overlay (белый силуэт внутри круга) — only without avatar -->
    <v-path
      v-if="iconPathData && !avatarImage"
      :config="iconConfig"
    />

    <!-- Label -->
    <v-text
      :config="{
        text: label,
        fontSize: 14,
        fontFamily: 'Arial',
        fill: 'white',
        align: 'center',
        x: -30,
        y: (30 * token.scale) + 5,
        width: 60,
        shadowColor: 'black',
        shadowBlur: 2,
        shadowOpacity: 1
      }"
    />
  </v-group>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { MapToken } from '@/types/models'
import { useCharactersStore } from '@/stores/characters'
import { useSessionStore } from '@/stores/session'
import { getTokenIcon } from '@/data/tokenIcons'

const props = defineProps<{
  token: MapToken
  selected?: boolean
  isReadOnly?: boolean
}>()

const emit = defineEmits<{
  (e: 'update', id: string, x: number, y: number): void
  (e: 'select', id: string): void
  (e: 'contextmenu', id: string, x: number, y: number): void
}>()

const charactersStore = useCharactersStore()
const sessionStore = useSessionStore()

const isOwnMovable = computed(() => {
  if (!props.token.character_id) return false
  const currentPlayer = sessionStore.currentPlayer
  if (!currentPlayer || currentPlayer.is_gm || !currentPlayer.can_move) return false
  const character = charactersStore.characters.find(c => c.id === props.token.character_id)
  return character?.player_id === sessionStore.playerId
})

const avatarSrc = computed(() => {
  if (!props.token.character_id) return null
  const char = charactersStore.characters.find(c => c.id === props.token.character_id)
  return char?.avatar_url || null
})

const avatarImage = ref<HTMLImageElement | null>(null)

watch(avatarSrc, (src) => {
  if (src) {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => { avatarImage.value = img }
    img.onerror = () => { avatarImage.value = null }
    img.src = src
  } else {
    avatarImage.value = null
  }
}, { immediate: true })

function clipCircle(ctx: any) {
  const r = 30 * props.token.scale
  ctx.arc(0, 0, r, 0, Math.PI * 2, false)
}

const iconDef = computed(() => props.token.icon ? getTokenIcon(props.token.icon) : null)
const iconPathData = computed(() => iconDef.value?.pathData ?? null)

const iconConfig = computed(() => {
  if (!iconPathData.value) return {}
  const tokenRadius = 30 * props.token.scale
  const iconSize = tokenRadius * 1.4
  const scaleFactor = iconSize / 512
  return {
    data: iconPathData.value,
    fill: 'white',
    opacity: 0.9,
    x: -iconSize / 2,
    y: -iconSize / 2,
    scaleX: scaleFactor,
    scaleY: scaleFactor,
    listening: false,
  }
})

const label = computed(() => {
  if (props.token.label) return props.token.label
  
  if (props.token.character_id) {
    const char = charactersStore.characters.find(c => c.id === props.token.character_id)
    return char ? char.name : 'Unknown'
  }
  
  return 'Token'
})

function onDragStart(e: any) {
  // Prevent event from bubbling to stage (предотвращаем случайный stage drag)
  e.cancelBubble = true
  e.target.moveToTop()
}

function onDragEnd(e: any) {
  // Prevent event from bubbling to stage
  e.cancelBubble = true
  emit('update', props.token.id, e.target.x(), e.target.y())
}

// Throttled update could be handled here or in parent
function onDragMove(e: any) {
  // Optional: Emit intermediate updates if needed for real-time sync
}

function onClick() {
  emit('select', props.token.id)
}

function onContextMenu(e: any) {
  e.evt.preventDefault()
  e.cancelBubble = true
  emit('contextmenu', props.token.id, e.evt.clientX, e.evt.clientY)
}
</script>
