<template>
  <router-view />
  <Toast />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { wsService } from '@/services/websocket'
import Toast from '@/components/common/Toast.vue'

const route = useRoute()
const sessionStore = useSessionStore()

function handleVisibilityChange() {
  if (document.visibilityState === 'visible') {
    const token = localStorage.getItem('token')

    if (token && !wsService.isConnected) {
      console.log('Tab visible, reconnecting...')
      wsService.resetReconnectCounter()

      const codeFromUrl = route.params.code as string | undefined
      sessionStore.tryRestoreSession(codeFromUrl)
    }
  }
}

onMounted(() => {
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style>
@import '@/assets/css/tokens.css';
@import '@/assets/css/base.css';
@import '@/assets/css/utilities.css';
</style>
