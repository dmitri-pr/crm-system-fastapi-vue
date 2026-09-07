<template>
  <div>
    <h2 class="fw-bold">Лиды</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="hstack gap-3 pb-4">
        <router-link v-if="auth.canManageLeads" to="/leads/new" class="btn btn-success p-2">Создать</router-link>
        <span v-if="error" class="alert alert-danger mb-0 py-1 px-2">{{ error }}</span>
      </div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <ul v-else class="list-group">
          <li v-for="lead in leads" :key="lead.id" class="list-group-item list-group-item-light d-flex justify-content-between align-items-center">
            <router-link :to="`/leads/${lead.id}`" class="text-decoration-none link-dark">{{ lead.last_name }} {{ lead.first_name }}</router-link>
            <div class="d-flex gap-2 align-items-center">
              <span v-if="lead.is_converted" class="badge bg-success">Конвертирован</span>
              <router-link v-else :to="`/customers/new?lead_id=${lead.id}`" class="btn btn-primary btn-sm">В клиенты</router-link>
              <button v-if="auth.canManageLeads" @click="remove(lead.id)" class="btn btn-danger btn-sm">Удалить</button>
            </div>
          </li>
          <li v-if="leads.length===0" class="list-group-item text-center text-muted">Нет лидов</li>
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
const leads=ref([])
const loading=ref(true)
const error=ref('')
async function load(){
  loading.value=true
  error.value=''
  try{ const res=await client.get('/leads'); leads.value=res.data }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e)}
  finally{loading.value=false}
}
async function remove(id){
  if(!confirm('Удалить лида?')) return
  try{ await client.delete(`/leads/${id}`); leads.value=leads.value.filter(l=>l.id!==id) }catch(e){ alert(e.response?.data?.detail||'Ошибка') }
}
onMounted(load)
</script>
