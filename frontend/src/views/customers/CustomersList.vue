<template>
  <div>
    <h2 class="fw-bold">Активные клиенты</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="hstack gap-3 pb-4">
        <router-link v-if="auth.canManageCustomers" to="/customers/new" class="btn btn-success p-2">Создать</router-link>
        <span v-if="error" class="alert alert-danger mb-0 py-1 px-2">{{ error }}</span>
      </div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <ul v-else class="list-group">
          <li v-for="c in customers" :key="c.id" class="list-group-item list-group-item-light d-flex justify-content-between align-items-center">
            <router-link :to="`/customers/${c.id}`" class="text-decoration-none link-dark">{{ c.lead?.last_name || '—' }} {{ c.lead?.first_name || '' }} — {{ c.contract?.name || '—' }}</router-link>
            <button v-if="auth.canManageCustomers" @click="remove(c.id)" class="btn btn-danger btn-sm">Удалить</button>
          </li>
          <li v-if="customers.length===0" class="list-group-item text-center text-muted">Нет активных клиентов</li>
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
const customers=ref([])
const loading=ref(true)
const error=ref('')
async function load(){
  loading.value=true
  error.value=''
  try{ const res=await client.get('/customers'); customers.value=res.data }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e)}
  finally{loading.value=false}
}
async function remove(id){
  if(!confirm('Удалить?')) return
  try{ await client.delete(`/customers/${id}`); customers.value=customers.value.filter(c=>c.id!==id)}catch(e){ alert(e.response?.data?.detail||'Ошибка') }
}
onMounted(load)
</script>
