<template>
  <div class="game-map-container" ref="container">
    <div v-if="!displayMap && !mapLoading" class="no-map">
      <p>Нет активной карты</p>
      <button v-if="isGm && !editorMode" @click="createTestMap" class="btn primary">Создать тестовую карту</button>
    </div>

    <div v-else-if="mapLoading" class="loading">
      Загрузка карты...
    </div>

    <v-stage
      v-else
      ref="stage"
      :config="stageConfig"
      @dragstart="handleDragStart"
      @dragend="handleDragEnd"
      @wheel="handleWheel"
      @contextmenu="handleStageContextMenu"
    >
      <v-layer ref="backgroundLayer">
        <!-- Background color fallback -->
        <v-rect
            :config="{
                x: 0,
                y: 0,
                width: displayMap!.width,
                height: displayMap!.height,
                fill: '#2c2c2c'
            }"
        />
        <!-- Background image -->
        <v-image
            v-if="bgImage"
            :config="{
                x: 0,
                y: 0,
                width: displayMap!.width,
                height: displayMap!.height,
                image: bgImage,
                listening: false
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
          v-for="token in displayMap!.tokens"
          :key="token.id"
          :token="token"
          :selected="selectedTokenId === token.id"
          :is-read-only="isTokenReadOnly(token)"
          @update="handleTokenUpdate"
          @select="handleTokenSelect"
          @contextmenu="handleTokenContextMenu"
        />
      </v-layer>
    </v-stage>

    <!-- Zoom Indicator (10.1) -->
    <Transition name="fade">
      <div v-if="showZoomIndicator" class="zoom-indicator">
        {{ Math.round(stageConfig.scaleX * 100) }}%
      </div>
    </Transition>

    <!-- Controls Toolbar -->
    <div class="map-toolbar">
      <div class="toolbar-group">
        <button class="toolbar-btn" @click="fitToScreen" title="Вписать в экран">
          <Maximize2 :size="18" />
        </button>
        <button class="toolbar-btn" @click="zoomIn" title="Приблизить">
          <ZoomIn :size="18" />
        </button>
        <button class="toolbar-btn" @click="zoomOut" title="Отдалить">
          <ZoomOut :size="18" />
        </button>
      </div>
      <div v-if="isGm" class="toolbar-divider" />
      <div v-if="isGm" class="toolbar-group">
        <button class="toolbar-btn toolbar-btn--accent" @click="showAddTokenModal = true" title="Добавить токен">
          <Plus :size="18" />
        </button>
        <button v-if="!editorMode" class="toolbar-btn" @click="saveToLibrary" title="Сохранить в библиотеку">
          <Save :size="18" />
        </button>
      </div>
    </div>

    <!-- Token Context Menu -->
    <Teleport to="body">
      <Transition name="ctx-menu">
        <div
          v-if="ctxMenu.visible"
          class="ctx-menu"
          :style="{ left: ctxMenu.x + 'px', top: ctxMenu.y + 'px' }"
          @click.stop
        >
          <button class="ctx-menu-item" @click="confirmAction('delete')">
            <Trash2 :size="16" />
            <span>Удалить</span>
          </button>
          <button
            v-if="ctxMenuToken?.type === 'character' && isNpcToken(ctxMenuToken) && combatStore.isActive"
            class="ctx-menu-item"
            @click="addNpcToCombat"
          >
            <Swords :size="16" />
            <span>Добавить в бой</span>
          </button>
          <button
            v-if="ctxMenuToken?.type === 'monster'"
            class="ctx-menu-item ctx-menu-item--danger"
            @click="confirmAction('kill')"
          >
            <Skull :size="16" />
            <span>Убить</span>
          </button>
        </div>
      </Transition>
    </Teleport>

    <!-- Confirm Modal -->
    <ConfirmModal
      v-model="showConfirmModal"
      :title="confirmTitle"
      :message="confirmMessage"
      :confirm-text="confirmBtnText"
      :danger="true"
      @confirm="executeConfirmedAction"
    />

    <!-- Add Token Modal -->
    <AddTokenModal
      v-model="showAddTokenModal"
      :hide-character-tab="editorMode"
      @add="handleAddToken"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import type { MapToken as MapTokenType, MapTokenCreate, GameMap as GameMapType } from '@/types/models'
import { useMapStore } from '@/stores/map'
import { useSessionStore } from '@/stores/session'
import { useCharactersStore } from '@/stores/characters'
import { useCombatStore } from '@/stores/combat'
import { mapsApi } from '@/services/api'
import { useToast } from '@/composables/useToast'
import { useThrottle } from '@/composables/useThrottle'
import { useIsMobile } from '@/composables/useIsMobile'
import { Maximize2, ZoomIn, ZoomOut, Plus, Trash2, Skull, Save, Swords } from 'lucide-vue-next'
import MapToken from './MapToken.vue'
import AddTokenModal from './AddTokenModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const props = defineProps<{
  isReadOnly?: boolean
  editorMode?: boolean
  editorMap?: GameMapType | null
}>()

const emit = defineEmits<{
  'editor-add-token': [data: MapTokenCreate]
  'editor-update-token': [tokenId: string, data: { x: number; y: number }]
  'editor-delete-token': [tokenId: string]
}>()

const mapStore = useMapStore()
const sessionStore = useSessionStore()
const charactersStore = useCharactersStore()
const combatStore = useCombatStore()
const toast = useToast()
const { isMobile } = useIsMobile()
const container = ref<HTMLElement | null>(null)
const stage = ref<any>(null)

const displayMap = computed<GameMapType | null>(() => {
  if (props.editorMode) return props.editorMap || null
  return mapStore.activeMap
})
const mapLoading = computed(() => props.editorMode ? false : mapStore.loading)
const isGm = computed(() => props.editorMode || sessionStore.isGm)
const selectedTokenId = ref<string | null>(null)
const showAddTokenModal = ref(false)

// Zoom indicator (10.1)
const showZoomIndicator = ref(false)
let zoomIndicatorTimeout: number | null = null

// Context menu state
const ctxMenu = reactive({ visible: false, x: 0, y: 0, tokenId: '' })
const ctxMenuToken = computed(() => {
  if (!ctxMenu.tokenId || !displayMap.value) return null
  return displayMap.value.tokens.find(t => t.id === ctxMenu.tokenId) || null
})
const showConfirmModal = ref(false)
const pendingAction = ref<'delete' | 'kill' | null>(null)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmBtnText = ref('')

function handleTokenContextMenu(id: string, x: number, y: number) {
  if (!isGm.value) return
  ctxMenu.visible = true
  ctxMenu.tokenId = id
  ctxMenu.x = x
  ctxMenu.y = y
  selectedTokenId.value = id
}

function closeCtxMenu() {
  ctxMenu.visible = false
}

function confirmAction(action: 'delete' | 'kill') {
  closeCtxMenu()
  pendingAction.value = action
  const tokenLabel = ctxMenuToken.value?.label || 'токен'
  if (action === 'kill') {
    confirmTitle.value = 'Подтверждение убийства'
    confirmMessage.value = `Убить «${tokenLabel}»? Токен будет удалён с карты.`
    confirmBtnText.value = 'Убить'
  } else {
    confirmTitle.value = 'Удаление токена'
    confirmMessage.value = `Удалить «${tokenLabel}» с карты?`
    confirmBtnText.value = 'Удалить'
  }
  showConfirmModal.value = true
}

async function executeConfirmedAction() {
  showConfirmModal.value = false
  if (!ctxMenu.tokenId) return
  try {
    if (props.editorMode) {
      emit('editor-delete-token', ctxMenu.tokenId)
    } else {
      await mapStore.deleteToken(ctxMenu.tokenId)
    }
  } catch {
    console.error('Failed to delete token')
  }
  selectedTokenId.value = null
  pendingAction.value = null
}

function isNpcToken(token: MapTokenType): boolean {
  if (!token.character_id) return false
  const character = charactersStore.characters.find(c => c.id === token.character_id)
  if (!character) return false
  const player = sessionStore.players.find(p => p.id === character.player_id)
  return player?.is_gm ?? false
}

async function addNpcToCombat() {
  if (!ctxMenuToken.value?.character_id) return
  closeCtxMenu()

  try {
    await combatStore.rollInitiativeForNpc(ctxMenuToken.value.character_id)
    toast.success('NPC добавлен в бой')
  } catch (error) {
    console.error('Failed to add NPC to combat:', error)
    toast.error('Не удалось добавить NPC в бой')
  }
}

function onGlobalClick() {
  if (ctxMenu.visible) closeCtxMenu()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && ctxMenu.visible) closeCtxMenu()
}

onMounted(() => {
  document.addEventListener('click', onGlobalClick)
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', onGlobalClick)
  document.removeEventListener('keydown', onKeydown)

  // Cleanup pinch events
  if (pinchContainer) {
    pinchContainer.removeEventListener('touchstart', handlePinchStart)
    pinchContainer.removeEventListener('touchmove', throttledPinchMove)
    pinchContainer.removeEventListener('touchend', handlePinchEnd)
    pinchContainer.removeEventListener('touchcancel', handlePinchEnd)
    cancelPinchThrottle()
  }

  // Cleanup zoom indicator timeout
  if (zoomIndicatorTimeout) {
    clearTimeout(zoomIndicatorTimeout)
  }
})

// Background image loading
const bgImage = ref<HTMLImageElement | null>(null)
const bgUrl = computed(() => displayMap.value?.background_url || null)

watch(bgUrl, (url) => {
  if (url) {
    const img = new window.Image()
    img.src = url
    img.onload = () => { bgImage.value = img }
    img.onerror = () => { bgImage.value = null }
  } else {
    bgImage.value = null
  }
}, { immediate: true })

const stageConfig = ref({
  width: 800,
  height: 600,
  scaleX: 1,
  scaleY: 1,
  x: 0,
  y: 0,
  draggable: true  // Работает на всех устройствах (cancelBubble в токенах предотвращает конфликт)
})

// Zoom indicator: показывать при изменении масштаба
watch(() => stageConfig.value.scaleX, () => {
  showZoomIndicator.value = true

  if (zoomIndicatorTimeout) clearTimeout(zoomIndicatorTimeout)
  zoomIndicatorTimeout = window.setTimeout(() => {
    showZoomIndicator.value = false
  }, 800)
})

// Pinch-to-zoom state
let lastPinchDist = 0
let lastPinchCenter: { x: number; y: number } | null = null

// 10.3: Ограничение границ карты (предотвращение выхода в пустоту)
function clampStagePosition() {
  if (!displayMap.value) return

  const mapWidth = displayMap.value.width
  const mapHeight = displayMap.value.height
  const viewportWidth = stageConfig.value.width
  const viewportHeight = stageConfig.value.height
  const scale = stageConfig.value.scaleX

  const scaledMapWidth = mapWidth * scale
  const scaledMapHeight = mapHeight * scale

  // Вычисляем границы для x
  // Если карта больше viewport: minX отрицательный, maxX = 0
  // Если карта меньше viewport: minX = 0, maxX положительный
  const minX = Math.min(viewportWidth - scaledMapWidth, 0)
  const maxX = Math.max(viewportWidth - scaledMapWidth, 0)

  // Вычисляем границы для y
  const minY = Math.min(viewportHeight - scaledMapHeight, 0)
  const maxY = Math.max(viewportHeight - scaledMapHeight, 0)

  // Clamp позицию
  stageConfig.value.x = Math.max(minX, Math.min(maxX, stageConfig.value.x))
  stageConfig.value.y = Math.max(minY, Math.min(maxY, stageConfig.value.y))
}

function getDistance(t1: Touch, t2: Touch): number {
  return Math.sqrt((t2.clientX - t1.clientX) ** 2 + (t2.clientY - t1.clientY) ** 2)
}

function getCenter(t1: Touch, t2: Touch): { x: number; y: number } {
  return { x: (t1.clientX + t2.clientX) / 2, y: (t1.clientY + t2.clientY) / 2 }
}

function handlePinchStart(e: TouchEvent) {
  if (e.touches.length !== 2) return
  e.preventDefault()

  const t1 = e.touches[0]
  const t2 = e.touches[1]

  lastPinchDist = getDistance(t1, t2)
  lastPinchCenter = getCenter(t1, t2)

  const stageNode = stage.value?.getStage()
  if (stageNode) {
    // Остановить stage drag
    if (stageNode.isDragging()) {
      stageNode.stopDrag()
    }

    // Остановить drag всех токенов при pinch
    stageNode.find('.draggable-token').forEach((node: any) => {
      if (node.isDragging()) {
        node.stopDrag()
      }
    })
  }
}

function handlePinchMove(e: TouchEvent) {
  if (e.touches.length !== 2) return
  e.preventDefault()

  const stageNode = stage.value?.getStage()
  if (!stageNode) return

  const t1 = e.touches[0]
  const t2 = e.touches[1]
  const newDist = getDistance(t1, t2)
  const newCenter = getCenter(t1, t2)

  // Skip first frame if not initialized
  if (lastPinchDist === 0 || !lastPinchCenter) {
    lastPinchDist = newDist
    lastPinchCenter = newCenter
    return
  }

  const oldScale = stageConfig.value.scaleX
  const scaleChange = newDist / lastPinchDist
  let newScale = oldScale * scaleChange
  newScale = Math.max(0.1, Math.min(newScale, 5))

  // Get pinch center in container coordinates
  const containerRect = stageNode.container().getBoundingClientRect()
  const pointerX = lastPinchCenter.x - containerRect.left
  const pointerY = lastPinchCenter.y - containerRect.top

  // Calculate point in stage coordinates BEFORE zoom
  const mousePointTo = {
    x: (pointerX - stageConfig.value.x) / oldScale,
    y: (pointerY - stageConfig.value.y) / oldScale,
  }

  // Apply new scale
  stageConfig.value.scaleX = newScale
  stageConfig.value.scaleY = newScale

  // Calculate new stage position (same math as handleWheel)
  stageConfig.value.x = pointerX - mousePointTo.x * newScale
  stageConfig.value.y = pointerY - mousePointTo.y * newScale

  // Ограничить позицию (10.3)
  clampStagePosition()

  lastPinchDist = newDist
  lastPinchCenter = newCenter
}

function handlePinchEnd() {
  lastPinchDist = 0
  lastPinchCenter = null
}

// Create throttled version of pinch move
const { throttled: throttledPinchMove, cancel: cancelPinchThrottle } = useThrottle(handlePinchMove)

// Resize observer to update stage dimensions
let pinchContainer: HTMLElement | null = null

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

  // Initial load (skip in editor mode)
  if (!props.editorMode) {
    mapStore.fetchSessionMaps()
    mapStore.setupWebSocketHandlers()
  }

  // Pinch zoom: native touch events on canvas container
  setTimeout(() => {
    const stageNode = stage.value?.getStage()
    if (stageNode) {
      pinchContainer = stageNode.container()
      pinchContainer!.addEventListener('touchstart', handlePinchStart, { passive: false })
      pinchContainer!.addEventListener('touchmove', throttledPinchMove, { passive: false })
      pinchContainer!.addEventListener('touchend', handlePinchEnd, { passive: false })
      pinchContainer!.addEventListener('touchcancel', handlePinchEnd, { passive: false })

      // Блокировать native iOS жесты (double-tap zoom, bounce scroll)
      const preventNativeTouch = (e: TouchEvent) => {
        // Блокируем только если касание canvas, не UI элементов
        if (e.target === pinchContainer || pinchContainer!.contains(e.target as Node)) {
          e.preventDefault()
        }
      }
      pinchContainer!.addEventListener('touchstart', preventNativeTouch, { passive: false })
    }
  }, 100)
})

// Grid generation
const gridLines = computed(() => {
  if (!displayMap.value) return []
  const lines = []
  const { width, height, grid_scale } = displayMap.value
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

  // Ограничить позицию (10.3)
  clampStagePosition()
}

function handleStageContextMenu(e: any) {
  e.evt.preventDefault()
  if (ctxMenu.visible) closeCtxMenu()
}

function handleDragStart() {
  // Stage drag start
}

function handleDragEnd() {
  // Stage drag end - ограничить позицию (10.3)
  clampStagePosition()
}

// Per-token read-only logic
function isTokenReadOnly(token: MapTokenType): boolean {
  if (props.editorMode) return false  // Editor — all tokens are draggable
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
  if (props.editorMode) {
    emit('editor-update-token', id, { x, y })
    return
  }
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
    if (!displayMap.value || !container.value) return
    const padding = 20
    const w = container.value.clientWidth - padding * 2
    const h = container.value.clientHeight - padding * 2

    const mapW = displayMap.value.width
    const mapH = displayMap.value.height

    const scale = Math.min(w / mapW, h / mapH)

    stageConfig.value.scaleX = scale
    stageConfig.value.scaleY = scale
    stageConfig.value.x = (container.value.clientWidth - mapW * scale) / 2
    stageConfig.value.y = (container.value.clientHeight - mapH * scale) / 2

    // Ограничить позицию (10.3)
    clampStagePosition()
}

function zoomToPoint(scaleChange: number) {
  if (!container.value) return

  const oldScale = stageConfig.value.scaleX
  let newScale = oldScale * scaleChange
  newScale = Math.max(0.1, Math.min(newScale, 5))

  // Get viewport center
  const viewW = stageConfig.value.width
  const viewH = stageConfig.value.height
  const centerX = viewW / 2
  const centerY = viewH / 2

  // Calculate point in stage coordinates BEFORE zoom
  const mousePointTo = {
    x: (centerX - stageConfig.value.x) / oldScale,
    y: (centerY - stageConfig.value.y) / oldScale,
  }

  // Apply new scale
  stageConfig.value.scaleX = newScale
  stageConfig.value.scaleY = newScale

  // Calculate new position to keep center fixed
  stageConfig.value.x = centerX - mousePointTo.x * newScale
  stageConfig.value.y = centerY - mousePointTo.y * newScale

  // Ограничить позицию (10.3)
  clampStagePosition()
}

function zoomIn() {
  zoomToPoint(1.2)
}

function zoomOut() {
  zoomToPoint(1 / 1.2)
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
    if (!displayMap.value) return

    // Calculate viewport center for initial placement
    const scale = stageConfig.value.scaleX
    const viewW = stageConfig.value.width
    const viewH = stageConfig.value.height
    const stageX = stageConfig.value.x
    const stageY = stageConfig.value.y
    const centerX = (viewW / 2 - stageX) / scale
    const centerY = (viewH / 2 - stageY) / scale

    const tokenData = {
        ...data,
        x: centerX,
        y: centerY,
        layer: 'tokens',
    }

    if (props.editorMode) {
        emit('editor-add-token', tokenData)
    } else {
        await mapStore.addToken(displayMap.value.id, tokenData)
    }
}

// Save map to library (session mode only)
async function saveToLibrary() {
    if (!displayMap.value || props.editorMode) return
    try {
        await mapsApi.saveToLibrary(displayMap.value.id)
        toast.success('Карта сохранена в библиотеку')
    } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Не удалось сохранить')
    }
}

</script>

<style scoped>
.game-map-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: var(--color-bg-tertiary, #0f0f1a);
  overflow: hidden;
  touch-action: none;  /* Полный контроль над touch жестами */
}

.no-map, .loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  gap: var(--spacing-3);
}

/* Toolbar */
.map-toolbar {
  position: absolute;
  bottom: var(--spacing-4);
  right: var(--spacing-4);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  background: var(--color-bg-secondary, #16213e);
  border: 1px solid var(--alpha-overlay-medium, rgba(255,255,255,0.1));
  padding: var(--spacing-1);
  border-radius: var(--radius-lg, 12px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}

.toolbar-group {
  display: flex;
  gap: var(--spacing-1);
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--alpha-overlay-medium, rgba(255,255,255,0.1));
  margin: 0 2px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--radius-md, 8px);
  background: transparent;
  color: var(--color-text-secondary, #a0a0a0);
  cursor: pointer;
  transition: all 150ms ease;
}

.toolbar-btn:hover {
  background: var(--alpha-overlay-light, rgba(255,255,255,0.05));
  color: var(--color-text-primary, #eaeaea);
}

.toolbar-btn:active {
  transform: scale(0.92);
}

.toolbar-btn--accent {
  color: var(--color-accent-primary, #e94560);
}

.toolbar-btn--accent:hover {
  background: rgba(233, 69, 96, 0.15);
  color: var(--color-accent-primary, #e94560);
}

/* Zoom Indicator (10.1) */
.zoom-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 12px 24px;
  border-radius: var(--radius-lg, 12px);
  font-size: 24px;
  font-weight: bold;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}

/* Fade transition для индикатора */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

<style>
/* Context menu (not scoped — teleported to body) */
.ctx-menu {
  position: fixed;
  z-index: 800;
  min-width: 160px;
  background: var(--color-bg-secondary, #16213e);
  border: 1px solid var(--alpha-overlay-medium, rgba(255,255,255,0.1));
  border-radius: var(--radius-md, 8px);
  padding: var(--spacing-1, 4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.ctx-menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2, 8px);
  width: 100%;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--color-text-secondary, #a0a0a0);
  font-size: 14px;
  cursor: pointer;
  transition: all 150ms ease;
}

.ctx-menu-item:hover {
  background: var(--alpha-overlay-light, rgba(255,255,255,0.05));
  color: var(--color-text-primary, #eaeaea);
}

.ctx-menu-item--danger {
  color: var(--color-danger, #ef4444);
}

.ctx-menu-item--danger:hover {
  background: rgba(239, 68, 68, 0.12);
  color: var(--color-danger, #ef4444);
}

.ctx-menu-enter-active,
.ctx-menu-leave-active {
  transition: all 100ms ease;
}

.ctx-menu-enter-from,
.ctx-menu-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
