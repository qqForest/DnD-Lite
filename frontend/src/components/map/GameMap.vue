<template>
  <div class="game-map-container" ref="container">
    <div v-if="!mapStore.activeMap && !mapStore.loading" class="no-map">
      <p>Нет активной карты</p>
      <button v-if="isGm" @click="createTestMap" class="btn primary">Создать тестовую карту</button>
    </div>
    
    <div v-else-if="mapStore.loading" class="loading">
      Загрузка карты...
    </div>

    <v-stage
      v-else
      ref="stage"
      :config="stageConfig"
      @dragstart="handleDragStart"
      @dragend="handleDragEnd"
      @wheel="handleWheel"
    >
      <v-layer ref="backgroundLayer">
        <!-- Background Image or Color -->
        <v-rect
            :config="{
                x: 0,
                y: 0,
                width: mapStore.activeMap!.width,
                height: mapStore.activeMap!.height,
                fill: '#2c2c2c' // Placeholder background
            }"
        />
        
        <!-- Grid -->
         <v-line
            v-for="line in gridLines"
            :key="line.id"
            :config="line.config"
         />
      </v-layer>

      <v-layer ref="tokenLayer">
        <MapToken
          v-for="token in mapStore.activeMap!.tokens"
          :key="token.id"
          :token="token"
          :selected="selectedTokenId === token.id"
          :is-read-only="isTokenReadOnly(token)"
          @update="handleTokenUpdate"
          @select="handleTokenSelect"
        />
      </v-layer>
    </v-stage>
    
    <!-- Controls Overlay -->
    <div class="map-controls">
        <button @click="fitToScreen">Fit</button>
        <button @click="zoomIn">+</button>
        <button @click="zoomOut">-</button>
        <button v-if="isGm" @click="showAddTokenModal = true" title="Add Token">+ Token</button>
    </div>

    <!-- Add Token Modal -->
    <AddTokenModal
      v-model="showAddTokenModal"
      @add="handleAddToken"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { MapToken as MapTokenType, MapTokenCreate } from '@/types/models'
import { useMapStore } from '@/stores/map'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import MapToken from './MapToken.vue'
import AddTokenModal from './AddTokenModal.vue'

const props = defineProps<{
  isReadOnly?: boolean
}>()

const mapStore = useMapStore()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const container = ref<HTMLElement | null>(null)

const isGm = computed(() => sessionStore.isGm)
const selectedTokenId = ref<string | null>(null)
const showAddTokenModal = ref(false)

const stageConfig = ref({
  width: 800,
  height: 600,
  scaleX: 1,
  scaleY: 1,
  x: 0,
  y: 0,
  draggable: true
})

// Resize observer to update stage dimensions
onMounted(() => {
  if (container.value) {
    const observer = new ResizeObserver(() => {
      if (container.value) {
        stageConfig.value.width = container.value.clientWidth
        stageConfig.value.height = container.value.clientHeight
      }
    })
    observer.observe(container.value)
  }
  
  // Initial load
  mapStore.fetchSessionMaps()
  mapStore.setupWebSocketHandlers()
})

// Grid generation
const gridLines = computed(() => {
  if (!mapStore.activeMap) return []
  const lines = []
  const { width, height, grid_scale } = mapStore.activeMap
  const color = 'rgba(255, 255, 255, 0.1)'
  
  // Vertical
  for (let i = 0; i <= width / grid_scale; i++) {
    lines.push({
      id: `v-${i}`,
      config: {
        points: [i * grid_scale, 0, i * grid_scale, height],
        stroke: color,
        strokeWidth: 1
      }
    })
  }
  
  // Horizontal
  for (let i = 0; i <= height / grid_scale; i++) {
    lines.push({
      id: `h-${i}`,
      config: {
        points: [0, i * grid_scale, width, i * grid_scale],
        stroke: color,
        strokeWidth: 1
      }
    })
  }
  
  return lines
})

// Stage Interaction
function handleWheel(e: any) {
  e.evt.preventDefault()
  
  const scaleBy = 1.1
  const stage = e.target.getStage()
  const oldScale = stage.scaleX()
  const pointer = stage.getPointerPosition()

  const mousePointTo = {
    x: (pointer.x - stage.x()) / oldScale,
    y: (pointer.y - stage.y()) / oldScale,
  }

  let newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy
  
  // Limit scale
  newScale = Math.max(0.1, Math.min(newScale, 5))

  stageConfig.value.scaleX = newScale
  stageConfig.value.scaleY = newScale

  const newPos = {
    x: pointer.x - mousePointTo.x * newScale,
    y: pointer.y - mousePointTo.y * newScale,
  }
  
  stageConfig.value.x = newPos.x
  stageConfig.value.y = newPos.y
}

function handleDragStart() {
  // Stage drag start
}

function handleDragEnd() {
  // Stage drag end
}

// Per-token read-only logic
function isTokenReadOnly(token: MapTokenType): boolean {
  if (!props.isReadOnly) return false  // GM — all tokens are draggable

  // Player: allow only own character's token when can_move is enabled
  const currentPlayer = sessionStore.currentPlayer
  if (!currentPlayer?.can_move) return true

  if (token.character_id) {
    const character = charactersStore.characters.find(c => c.id === token.character_id)
    if (character && character.player_id === sessionStore.playerId) {
      return false  // Own token is draggable
    }
  }
  return true
}

// Token Interaction
async function handleTokenUpdate(id: string, x: number, y: number) {
  try {
    await mapStore.updateToken(id, { x, y })
  } catch (error: any) {
    if (error?.response?.status === 403) {
      console.warn('Not authorized to move this token')
      await mapStore.fetchSessionMaps()
    }
  }
}

function handleTokenSelect(id: string) {
  selectedTokenId.value = id
}

// Controls
function fitToScreen() {
    if (!mapStore.activeMap || !container.value) return
    const padding = 20
    const w = container.value.clientWidth - padding * 2
    const h = container.value.clientHeight - padding * 2
    
    const mapW = mapStore.activeMap.width
    const mapH = mapStore.activeMap.height
    
    const scale = Math.min(w / mapW, h / mapH)
    
    stageConfig.value.scaleX = scale
    stageConfig.value.scaleY = scale
    stageConfig.value.x = (container.value.clientWidth - mapW * scale) / 2
    stageConfig.value.y = (container.value.clientHeight - mapH * scale) / 2
}

function zoomIn() {
    stageConfig.value.scaleX *= 1.2
    stageConfig.value.scaleY *= 1.2
}

function zoomOut() {
    stageConfig.value.scaleX /= 1.2
    stageConfig.value.scaleY /= 1.2
}

// Map creation (keep for no-map state)
async function createTestMap() {
    await mapStore.createMap({
        name: 'Battle Map 1',
        width: 1000,
        height: 1000,
        grid_scale: 50
    })
    if (mapStore.maps.length > 0) {
        await mapStore.setActiveMap(mapStore.maps[mapStore.maps.length - 1].id)
    }
}

// Add token from modal
async function handleAddToken(data: MapTokenCreate) {
    if (!mapStore.activeMap) return

    // Calculate viewport center for initial placement
    const scale = stageConfig.value.scaleX
    const viewW = stageConfig.value.width
    const viewH = stageConfig.value.height
    const stageX = stageConfig.value.x
    const stageY = stageConfig.value.y
    const centerX = (viewW / 2 - stageX) / scale
    const centerY = (viewH / 2 - stageY) / scale

    await mapStore.addToken(mapStore.activeMap.id, {
        ...data,
        x: centerX,
        y: centerY,
        layer: 'tokens',
    })
}

</script>

<style scoped>
.game-map-container {
    width: 100%;
    height: 100%;
    position: relative;
    background: #1a1a1a;
    overflow: hidden;
}

.no-map, .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: white;
}

.map-controls {
    position: absolute;
    bottom: 20px;
    right: 20px;
    display: flex;
    gap: 10px;
    background: rgba(0,0,0,0.5);
    padding: 10px;
    border-radius: 8px;
}

button {
    padding: 5px 10px;
    cursor: pointer;
}
</style>
