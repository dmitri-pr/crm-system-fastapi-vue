<template>
  <div>
    <h2 class="fw-bold">Рекламные кампании</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="hstack gap-3 pb-4">
        <router-link v-if="auth.canManageAds" to="/ads/new" class="btn btn-success p-2">Создать</router-link>
        <router-link to="/ads/statistic" class="btn btn-primary p-2">Статистика</router-link>
        <span v-if="error" class="alert alert-danger mb-0 py-1 px-2">{{ error }}</span>
      </div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <ul v-else class="list-group">
          <li v-for="ad in ads" :key="ad.id" class="list-group-item list-group-item-light d-flex justify-content-between align-items-center">
            <div>
              <router-link :to="`/ads/${ad.id}`" class="text-decoration-none link-dark fw-bold">{{ ad.name }}</router-link>
              <small class="text-muted d-block">{{ ad.product_name }} | {{ ad.promotion_channel }} | {{ ad.budget }} руб</small>
            </div>
            <button @click="remove(ad.id)" class="btn btn-danger btn-sm">Удалить</button>
          </li>
          <li v-if="ads.length===0" class="list-group-item text-center text-muted">Нет кампаний</li>
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
const ads = ref([])
const loading = ref(true)
const error = ref('')

async function load(){
  loading.value=true
  error.value=''
  try{
    const res = await client.get('/ads')
    ads.value = res.data
  }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e)}
  finally{loading.value=false}
}
async function remove(id){
  if(!confirm('Удалить?')) return
  try{
    await client.delete(`/ads/${id}`)
    ads.value = ads.value.filter(a=>a.id!==id)
  }catch(e){ alert(e.response?.data?.detail || 'Ошибка') }
}
onMounted(load)
</script>
