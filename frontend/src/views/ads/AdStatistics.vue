<template>
  <div>
    <h2 class="fw-bold">Статистика рекламных кампаний</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <ul v-else class="list-group">
          <li v-for="ad in stats" :key="ad.id" class="list-group-item list-group-item-light d-flex justify-content-between align-items-center">
            <router-link :to="`/ads/${ad.id}`" class="text-decoration-none link-dark fw-bold">{{ ad.name }}</router-link>
            <span>Лидов: {{ ad.leads_count }} | Активных клиентов: {{ ad.customers_count }} | Соотношение дохода к затратам: {{ ad.profit !== null ? ad.profit : '-' }}</span>
          </li>
          <li v-if="stats.length===0" class="list-group-item text-center text-muted">Нет данных</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../../api/client'

const stats=ref([])
const loading=ref(true)
const error=ref('')
onMounted(async()=>{
  try{
    const res=await client.get('/ads/statistic')
    stats.value=res.data
  }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки статистики'; console.error(e) }
  finally{ loading.value=false }
})
</script>
