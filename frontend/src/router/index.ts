import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue')
    },
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresUser: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresUser: true }
    },
    {
      path: '/join',
      name: 'join',
      component: () => import('@/views/JoinSessionView.vue'),
      meta: { requiresUser: true }
    },
    {
      path: '/profile/characters/create',
      name: 'create-character',
      component: () => import('@/views/CreateCharacterView.vue'),
      meta: { requiresUser: true }
    },
    {
      path: '/profile/characters/:id/edit',
      name: 'edit-character',
      component: () => import('@/views/EditCharacterView.vue'),
      meta: { requiresUser: true }
    },
    {
      path: '/profile/maps/create',
      name: 'create-map',
      component: () => import('@/views/CreateMapView.vue'),
      meta: { requiresUser: true }
    },
    {
      path: '/profile/maps/:id/edit',
      name: 'edit-map',
      component: () => import('@/views/EditMapView.vue'),
      meta: { requiresUser: true }
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
  const authStore = useAuthStore()
  const sessionStore = useSessionStore()

  // Если требуется авторизация пользователя (не сессии)
  if (to.meta.requiresUser && !authStore.isLoggedIn) {
    next({ name: 'login' })
    return
  }

  // Если пользователь уже залогинен и идёт на login/register — редирект на home
  if ((to.name === 'login' || to.name === 'register') && authStore.isLoggedIn) {
    next({ name: 'dashboard' })
    return
  }

  if (to.meta.requiresAuth && !sessionStore.isAuthenticated) {
    next({ name: 'dashboard' })
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
      next({ name: 'dashboard' })
    }
  } else if (to.meta.role === 'player' && sessionStore.isGm) {
    next({ name: 'gm' })
  } else {
    next()
  }
})

export default router
