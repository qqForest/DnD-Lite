<template>
  <div class="auth-view">
    <div class="container">
      <h1 class="title">DnD Lite GM</h1>
      <p class="subtitle">Войдите в свой аккаунт</p>

      <BasePanel variant="elevated" class="auth-panel">
        <template #header>
          <h3>Вход</h3>
        </template>
        <div class="panel-content">
          <form ref="formRef" class="form" autocomplete="on" @submit.prevent="handleLogin">
            <BaseInput
              v-model="username"
              name="username"
              autocomplete="username"
              placeholder="Имя пользователя"
            />
            <BaseInput
              v-model="password"
              name="password"
              type="password"
              autocomplete="current-password"
              placeholder="Пароль"
            />
            <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
            <BaseButton
              variant="primary"
              size="lg"
              type="submit"
              :disabled="loading"
            >
              Войти
            </BaseButton>
          </form>
          <p class="switch-link">
            Нет аккаунта?
            <router-link to="/register">Зарегистрироваться</router-link>
          </p>
        </div>
      </BasePanel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const formRef = ref<HTMLFormElement | null>(null)

const canLogin = computed(() => {
  return username.value.trim().length > 0 && password.value.length >= 6
})

async function handleLogin() {
  if (loading.value) return

  // Читаем значения из DOM (браузерный autofill может не обновить Vue refs)
  let user = username.value
  let pass = password.value
  if (formRef.value) {
    const formData = new FormData(formRef.value)
    user = (formData.get('username') as string) || user
    pass = (formData.get('password') as string) || pass
  }

  if (!user.trim() || pass.length < 6) {
    errorMsg.value = 'Введите имя пользователя и пароль (мин. 6 символов)'
    return
  }

  loading.value = true
  errorMsg.value = ''
  try {
    await authStore.login(user.trim(), pass)
    router.push({ name: 'dashboard' })
  } catch (error: any) {
    errorMsg.value = error.response?.data?.detail || 'Не удалось войти. Проверьте данные.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--spacing-4);
  background: var(--color-bg-primary);
}

.container {
  width: 100%;
  max-width: 440px;
}

.title {
  text-align: center;
  font-size: var(--font-size-4xl);
  margin-bottom: var(--spacing-2);
  color: var(--color-text-primary);
}

.subtitle {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-8);
}

.auth-panel {
  width: 100%;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.error-msg {
  color: var(--color-danger, #e74c3c);
  font-size: var(--font-size-sm);
  margin: 0;
}

.switch-link {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.switch-link a {
  color: var(--color-accent, #7c6fe0);
  text-decoration: none;
}

.switch-link a:hover {
  text-decoration: underline;
}
</style>
