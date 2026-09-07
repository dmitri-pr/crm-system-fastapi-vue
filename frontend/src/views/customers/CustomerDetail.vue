<template>
  <div>
    <h2 class="fw-bold">Детальная информация об активном клиенте</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <div v-else-if="customer" class="card border-dark shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold">{{ customer.lead?.last_name || '—' }} {{ customer.lead?.first_name || '' }} {{ customer.lead?.patronymic || '' }}</h5>
            <p class="card-text">{{ customer.lead?.phone || '—' }}</p>
            <div class="mb-2">{{ customer.lead?.email || '—' }}</div>
            <div class="mb-2">Контракт: <router-link v-if="customer.contract" :to="`/contracts/${customer.contract.id}`">{{ customer.contract.name }}</router-link><span v-else>—</span> — {{ customer.contract?.cost ?? '—' }} руб</div>
            <div class="d-flex justify-content-center gap-2 mt-3">
              <router-link :to="`/customers/${customer.id}/edit`" class="btn btn-primary">Редактировать</router-link>
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
const customer=ref(null)
const loading=ref(true)
const error=ref('')
onMounted(async()=>{
  try{ const res=await client.get(`/customers/${route.params.id}`); customer.value=res.data }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e)}
  finally{loading.value=false}
})
async function remove(){
  if(!confirm('Удалить?')) return
  try{ await client.delete(`/customers/${customer.value.id}`); router.push('/customers')}catch(e){ alert(e.response?.data?.detail||'Ошибка')}
}
</script>
