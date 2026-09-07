<template>
  <div>
    <h2 class="fw-bold">Общая статистика</h2>
    <div v-if="loading" class="text-center py-5">Загрузка...</div>
    <div v-else class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col">
        <div class="card border-light shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold"><router-link to="/products" class="link-dark text-decoration-none">Услуг</router-link></h5>
            <i class="fas fa-microchip float-end fs-1"></i>
            <p class="card-text fw-bold fs-1">{{ stats.products_count }}</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card border-light shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold"><router-link to="/ads" class="link-dark text-decoration-none">Рекламных компаний</router-link></h5>
            <i class="fas fa-ad float-end fs-1"></i>
            <p class="card-text fw-bold fs-1">{{ stats.advertisements_count }}</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card border-light shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold"><router-link to="/leads" class="link-dark text-decoration-none">Лидов</router-link></h5>
            <i class="fas fa-user-clock float-end fs-1"></i>
            <p class="card-text fw-bold fs-1">{{ stats.leads_count }}</p>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="card border-light shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold"><router-link to="/customers" class="link-dark text-decoration-none">Активных клиентов</router-link></h5>
            <i class="fas fa-user-check float-end fs-1"></i>
            <p class="card-text fw-bold fs-1">{{ stats.customers_count }}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="px-4">
      <p class="text-muted">Добро пожаловать, <strong>{{ auth.user?.username }}</strong>! Ваша роль: <span class="badge bg-primary">{{ auth.user?.role }}</span></p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const stats = ref({ products_count: 0, advertisements_count: 0, leads_count: 0, customers_count: 0 })
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await client.get('/stats/dashboard')
    stats.value = res.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка загрузки статистики'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>
