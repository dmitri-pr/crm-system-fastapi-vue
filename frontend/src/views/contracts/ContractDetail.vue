<template>
  <div>
    <h2 class="fw-bold">Детальная информация о контракте</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <div v-else-if="contract" class="card border-dark shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold">{{ contract.name }}</h5>
            <p class="card-text">{{ contract.product_name }}. С {{ contract.start_date }} по {{ contract.end_date }}</p>
            <div v-if="contract.document" class="mb-2"><a :href="contract.document" target="_blank" class="btn btn-sm btn-outline-primary">Скачать документ</a></div>
            <div class="d-flex justify-content-end fw-bold">{{ contract.cost }} руб</div>
            <div class="d-flex justify-content-center gap-2 mt-3">
              <router-link :to="`/contracts/${contract.id}/edit`" class="btn btn-primary">Редактировать</router-link>
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
const contract=ref(null)
const loading=ref(true)
const error=ref('')
onMounted(async()=>{
  try{ const res=await client.get(`/contracts/${route.params.id}`); contract.value=res.data }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e)}
  finally{loading.value=false}
})
async function remove(){
  if(!confirm('Удалить?')) return
  try{ await client.delete(`/contracts/${contract.value.id}`); router.push('/contracts')}catch(e){ alert(e.response?.data?.detail||'Ошибка')}
}
</script>
