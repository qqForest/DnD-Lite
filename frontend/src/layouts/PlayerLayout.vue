<template>
  <div class="player-layout">
    <div class="top-bar">
      <slot name="topbar" />
    </div>
    <main class="main-area">
      <slot />
    </main>
    <div class="bottom-section">
      <slot name="bottom" />
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.player-layout {
  display: grid;
  grid-template-areas:
    "top"
    "main"
    "bottom";
  grid-template-rows: 44px 1fr auto;
  height: 100vh;
  height: 100dvh; /* Dynamic viewport for mobile */
  overflow: hidden;
}

.top-bar {
  grid-area: top;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--alpha-overlay-medium);
  z-index: var(--z-fixed);
}

.main-area {
  grid-area: main;
  overflow: hidden;
  background: var(--color-bg-primary);
}

.bottom-section {
  grid-area: bottom;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--alpha-overlay-medium);
}

@media (min-width: 1024px) {
  .player-layout {
    grid-template-areas:
      "top    top"
      "main   sheet"
      "bottom sheet";
    grid-template-columns: 1fr 320px;
    grid-template-rows: 48px 1fr auto;
  }

  .bottom-section {
    border-right: 1px solid var(--alpha-overlay-medium);
  }
}
</style>
