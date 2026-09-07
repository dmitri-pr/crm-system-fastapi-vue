<template>
  <div class="container mt-5">
    <div class="row d-flex justify-content-center">
      <div class="col-md-6">
        <div class="card px-5 py-5 shadow">
          <h3 class="text-center mb-4">Авторизация</h3>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label">Имя пользователя</label>
              <input v-model="username" class="form-control" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Пароль</label>
              <input v-model="password" type="password" class="form-control" required />
            </div>
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              {{ loading ? 'Вход...' : 'Войти' }}
            </button>
          </form>
          <div class="mt-4 small text-muted">
            <strong>Демо аккаунты:</strong><br/>
            admin / admin123 (админ)<br/>
            operator1 / operator123<br/>
            marketer1 / marketer123<br/>
            manager1 / manager123
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>
