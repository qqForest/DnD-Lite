import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '@/stores/session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/gm/lobby',
      name: 'gm-lobby',
      component: () => import('@/views/GMLobbyView.vue'),
      meta: { requiresAuth: true, role: 'gm' }
    },
    {
      path: '/gm',
      name: 'gm',
      component: () => import('@/views/GMView.vue'),
      meta: { requiresAuth: true, role: 'gm' }
    },
    {
      path: '/play/lobby',
      name: 'player-lobby',
      component: () => import('@/views/PlayerLobbyView.vue'),
      meta: { requiresAuth: true, role: 'player' }
    },
    {
      path: '/play',
      name: 'player',
      component: () => import('@/views/PlayerView.vue'),
      meta: { requiresAuth: true, role: 'player' }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const sessionStore = useSessionStore()

  if (to.meta.requiresAuth && !sessionStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  // Загружаем состояние сессии если нужно проверить session_started
  if ((to.meta.role === 'gm' || to.meta.role === 'player') && sessionStore.isAuthenticated && sessionStore.token) {
    if (!sessionStore.sessionState) {
      await sessionStore.fetchSessionState()
    }

    // Логика для GM
    if (to.meta.role === 'gm') {
      // Если GM идет на /gm и сессия не начата - редирект на лобби
      if (to.name === 'gm' && !sessionStore.sessionStarted) {
        next({ name: 'gm-lobby' })
        return
      }

      // Если GM идет на /gm/lobby и сессия уже начата - редирект на основной интерфейс
      if (to.name === 'gm-lobby' && sessionStore.sessionStarted) {
        next({ name: 'gm' })
        return
      }
    }

    // Логика для игроков
    if (to.meta.role === 'player') {
      // Если игрок идет на /play и сессия не начата - редирект на лобби
      if (to.name === 'player' && !sessionStore.sessionStarted) {
        next({ name: 'player-lobby' })
        return
      }

      // Если игрок идет на /play/lobby и сессия уже начата - редирект на основной интерфейс
      if (to.name === 'player-lobby' && sessionStore.sessionStarted) {
        next({ name: 'player' })
        return
      }
    }
  }

  if (to.meta.role === 'gm' && !sessionStore.isGm) {
    if (sessionStore.isAuthenticated) {
      next({ name: 'player' })
    } else {
      next({ name: 'home' })
    }
  } else if (to.meta.role === 'player' && sessionStore.isGm) {
    next({ name: 'gm' })
  } else {
    next()
  }
})

export default router
