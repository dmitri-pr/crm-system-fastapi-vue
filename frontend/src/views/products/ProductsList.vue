<template>
  <div>
    <h2 class="fw-bold">Услуги</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="hstack gap-3 pb-4">
        <router-link v-if="auth.canManageProducts" to="/products/new" class="btn btn-success p-2">Создать</router-link>
        <div v-if="error" class="alert alert-danger mb-0 py-1 px-2">{{ error }}</div>
      </div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <ul v-else class="list-group">
          <li v-for="p in products" :key="p.id" class="list-group-item list-group-item-light d-flex justify-content-between align-items-center">
            <router-link :to="`/products/${p.id}`" class="text-decoration-none link-dark">{{ p.name }} — {{ p.cost }} руб</router-link>
            <button @click="remove(p.id)" class="btn btn-danger btn-sm">Удалить</button>
          </li>
          <li v-if="products.length===0" class="list-group-item text-muted text-center">Нет услуг</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../../api/client'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const products = ref([])
const loading = ref(true)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await client.get('/products')
    products.value = res.data
  } catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e) }
  finally { loading.value=false }
}
async function remove(id){
  if(!confirm('Удалить услугу?')) return
  try {
    await client.delete(`/products/${id}`)
    products.value = products.value.filter(p=>p.id!==id)
  } catch(e){
    alert(e.response?.data?.detail || 'Ошибка удаления')
  }
}
onMounted(load)
</script>
