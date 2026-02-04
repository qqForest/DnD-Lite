<template>
  <div class="gm-layout">
    <div class="top-bar">
      <TopBar @leave="$emit('leave')" />
    </div>
    <div class="initiative-bar">
      <slot name="initiative-bar" />
    </div>
    <div class="left-panel">
      <LeftPanel />
    </div>
    <main class="main-area">
      <slot />
    </main>
    <div class="bottom-bar">
      <BottomBar />
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  leave: []
}>()

import TopBar from '@/components/gm/TopBar.vue'
import LeftPanel from '@/components/gm/LeftPanel.vue'
import BottomBar from '@/components/gm/BottomBar.vue'
</script>

<style scoped>
.gm-layout {
  display: grid;
  grid-template-areas:
    "top    top"
    "init   init"
    "left   main"
    "bottom bottom";
  grid-template-columns: var(--panel-width-md) 1fr;
  grid-template-rows: var(--panel-height-top) auto 1fr var(--panel-height-bottom);
  height: 100vh;
  overflow: hidden;
}

.top-bar {
  grid-area: top;
}

.initiative-bar {
  grid-area: init;
}

.left-panel {
  grid-area: left;
}

.main-area {
  grid-area: main;
  overflow: hidden;
  background: var(--color-bg-tertiary);
}

.bottom-bar {
  grid-area: bottom;
}

@media (max-width: 1024px) {
  .gm-layout {
    grid-template-areas:
      "top"
      "init"
      "main"
      "left"
      "bottom";
    grid-template-columns: 1fr;
    grid-template-rows: var(--panel-height-top) auto 1fr auto var(--panel-height-bottom);
  }

  .left-panel {
    position: fixed;
    bottom: var(--panel-height-bottom);
    left: 0;
    right: 0;
    max-height: 50vh;
    z-index: var(--z-fixed);
    background: var(--color-bg-secondary);
    border-top: 1px solid var(--alpha-overlay-light);
  }
}
</style>
