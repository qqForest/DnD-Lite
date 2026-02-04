<template>
  <div class="auth-view">
    <div class="container">
      <h1 class="title">DnD Lite GM</h1>
      <p class="subtitle">Создайте аккаунт</p>

      <BasePanel variant="elevated" class="auth-panel">
        <template #header>
          <h3>Регистрация</h3>
        </template>
        <div class="panel-content">
          <form ref="formRef" class="form" autocomplete="on" @submit.prevent="handleRegister">
            <BaseInput
              v-model="displayName"
              name="name"
              autocomplete="name"
              placeholder="Отображаемое имя"
            />
            <BaseInput
              v-model="username"
              name="username"
              autocomplete="username"
              placeholder="Имя пользователя (логин)"
            />
            <BaseInput
              v-model="password"
              name="password"
              type="password"
              autocomplete="new-password"
              placeholder="Пароль (минимум 6 символов)"
            />
            <div class="role-select">
              <label class="role-label">Роль:</label>
              <div class="role-options">
                <button
                  type="button"
                  class="role-option"
                  :class="{ active: role === 'player' }"
                  @click="role = 'player'"
                >
                  Игрок
                </button>
                <button
                  type="button"
                  class="role-option"
                  :class="{ active: role === 'gm' }"
                  @click="role = 'gm'"
                >
                  Game Master
                </button>
              </div>
            </div>
            <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
            <BaseButton
              variant="primary"
              size="lg"
              type="submit"
              :disabled="loading"
            >
              Зарегистрироваться
            </BaseButton>
          </form>
          <p class="switch-link">
            Уже есть аккаунт?
            <router-link to="/login">Войти</router-link>
          </p>
        </div>
      </BasePanel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BasePanel from '@/components/common/BasePanel.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<HTMLFormElement | null>(null)
const displayName = ref('')
const username = ref('')
const password = ref('')
const role = ref<'player' | 'gm'>('player')
const loading = ref(false)
const errorMsg = ref('')

async function handleRegister() {
  if (loading.value) return

  // Читаем из DOM на случай автозаполнения
  let name = displayName.value
  let user = username.value
  let pass = password.value
  if (formRef.value) {
    const formData = new FormData(formRef.value)
    name = (formData.get('name') as string) || name
    user = (formData.get('username') as string) || user
    pass = (formData.get('password') as string) || pass
  }

  if (!name.trim() || user.trim().length < 3 || pass.length < 6) {
    errorMsg.value = 'Заполните все поля (username мин. 3, пароль мин. 6 символов)'
    return
  }

  loading.value = true
  errorMsg.value = ''
  try {
    await authStore.register(user.trim(), name.trim(), pass, role.value)
    router.push({ name: 'home' })
  } catch (error: any) {
    errorMsg.value = error.response?.data?.detail || 'Не удалось зарегистрироваться. Попробуйте другой username.'
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

.role-select {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.role-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.role-options {
  display: flex;
  gap: var(--spacing-2);
}

.role-option {
  flex: 1;
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border, rgba(255, 255, 255, 0.1));
  border-radius: var(--radius-md, 8px);
  background: var(--color-bg-secondary, rgba(255, 255, 255, 0.05));
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: var(--font-size-sm);
}

.role-option:hover {
  border-color: var(--color-accent, #7c6fe0);
}

.role-option.active {
  border-color: var(--color-accent, #7c6fe0);
  background: rgba(124, 111, 224, 0.15);
  color: var(--color-text-primary);
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
