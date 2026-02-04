<template>
  <v-group
    :config="{
      x: token.x,
      y: token.y,
      draggable: !isReadOnly,
      id: token.id
    }"
    @dragstart="onDragStart"
    @dragend="onDragEnd"
    @dragmove="onDragMove"
    @click="onClick"
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

    <!-- Token Body -->
    <v-circle
      :config="{
        radius: 30 * token.scale,
        fill: token.color || '#cccccc',
        stroke: 'black',
        strokeWidth: 1,
        shadowBlur: 5
      }"
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
import { computed } from 'vue'
import type { MapToken } from '@/types/models'
import { useCharactersStore } from '@/stores/characters'

const props = defineProps<{
  token: MapToken
  selected?: boolean
  isReadOnly?: boolean
}>()

const emit = defineEmits<{
  (e: 'update', id: string, x: number, y: number): void
  (e: 'select', id: string): void
}>()

const charactersStore = useCharactersStore()

const label = computed(() => {
  if (props.token.label) return props.token.label
  
  if (props.token.character_id) {
    const char = charactersStore.characters.find(c => c.id === props.token.character_id)
    return char ? char.name : 'Unknown'
  }
  
  return 'Token'
})

function onDragStart(e: any) {
  e.target.moveToTop()
}

function onDragEnd(e: any) {
  emit('update', props.token.id, e.target.x(), e.target.y())
}

// Throttled update could be handled here or in parent
function onDragMove(e: any) {
  // Optional: Emit intermediate updates if needed for real-time sync
}

function onClick() {
  emit('select', props.token.id)
}
</script>
