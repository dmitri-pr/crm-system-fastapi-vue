<template>
  <div>
    <h2 class="fw-bold">Детальная информация о лиде</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <div v-else-if="lead" class="card border-dark shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold">{{ lead.last_name }} {{ lead.first_name }} {{ lead.patronymic }}</h5>
            <p class="card-text">{{ lead.phone }}</p>
            <div class="mb-2">{{ lead.email }}</div>
            <div class="mb-2 small text-muted">Рекламная кампания: {{ lead.advertisement_name || '-' }}</div>
            <div v-if="lead.is_converted" class="badge bg-success mb-2">Уже конвертирован в клиента</div>
            <div class="d-flex justify-content-center gap-2 fw-bold">
              <router-link :to="`/leads/${lead.id}/edit`" class="btn btn-primary">Редактировать</router-link>
              <router-link v-if="!lead.is_converted" :to="`/customers/new?lead_id=${lead.id}`" class="btn btn-success">В клиенты</router-link>
              <button @click="remove" class="btn btn-danger">Удалить</button>
            </div>
          </div>
        </div>
      </div>
      <div class="col"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../../api/client'

const route=useRoute()
const router=useRouter()
const lead=ref(null)
const loading=ref(true)
const error=ref('')
onMounted(async()=>{
  try{ const res=await client.get(`/leads/${route.params.id}`); lead.value=res.data }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e)}
  finally{loading.value=false}
})
async function remove(){
  if(!confirm('Удалить?')) return
  try{ await client.delete(`/leads/${lead.value.id}`); router.push('/leads') }catch(e){ alert(e.response?.data?.detail||'Ошибка')}
}
</script>
