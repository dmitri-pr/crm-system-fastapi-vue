<template>
  <div>
    <h2 class="fw-bold">Детальная информация о рекламной кампании</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <div v-else-if="ad" class="card border-dark shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold">{{ ad.name }}</h5>
            <p class="card-text">Услуга: {{ ad.product_name }}</p>
            <p class="card-text">Канал: {{ ad.promotion_channel }}</p>
            <div class="d-flex justify-content-end fw-bold">{{ ad.budget }} руб</div>
            <div class="d-flex justify-content-center gap-2 mt-3">
              <router-link :to="`/ads/${ad.id}/edit`" class="btn btn-primary">Редактировать</router-link>
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
const ad=ref(null)
const loading=ref(true)
const error=ref('')
onMounted(async()=>{
  try{
    const res=await client.get(`/ads/${route.params.id}`)
    ad.value=res.data
  }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e)}
  finally{loading.value=false}
})
async function remove(){
  if(!confirm('Удалить?')) return
  try{ await client.delete(`/ads/${ad.value.id}`); router.push('/ads') }catch(e){ alert(e.response?.data?.detail||'Ошибка')}
}
</script>
