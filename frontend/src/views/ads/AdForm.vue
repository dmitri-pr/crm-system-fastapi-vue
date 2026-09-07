<template>
  <div>
    <h2 class="fw-bold">{{ isEdit ? 'Редактирование рекламной кампании' : 'Создание рекламной кампании' }}</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Название</label>
            <input v-model="form.name" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Услуга</label>
            <select v-model.number="form.product_id" class="form-select" required>
              <option :value="null" disabled>Выберите услугу</option>
              <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }} — {{ p.cost }} руб</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Канал продвижения</label>
            <input v-model="form.promotion_channel" class="form-control" required placeholder="Яндекс Директ, VK, Google Ads..." />
          </div>
          <div class="mb-3">
            <label class="form-label">Бюджет (руб)</label>
            <input v-model.number="form.budget" type="number" step="0.01" class="form-control" required />
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '...' : (isEdit ? 'Применить' : 'Создать') }}</button>
          <router-link to="/ads" class="btn btn-secondary ms-2">Назад</router-link>
        </form>
      </div>
      <div class="col"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../../api/client'

const route=useRoute()
const router=useRouter()
const isEdit=computed(()=>!!route.params.id)
const loading=ref(false)
const error=ref('')
const products=ref([])
const form=reactive({ name:'', product_id: null, promotion_channel:'', budget:0 })

async function loadProducts(){
  try{
    const res=await client.get('/products')
    products.value=res.data
  }catch(e){ error.value = 'Не удалось загрузить услуги'; console.error(e)}
}
onMounted(async()=>{
  await loadProducts()
  if(isEdit.value){
    try{
      const res=await client.get(`/ads/${route.params.id}`)
      form.name = res.data.name || ''
      form.product_id = res.data.product_id ?? null
      form.promotion_channel = res.data.promotion_channel || ''
      form.budget = res.data.budget ?? 0
    }catch(e){ error.value = e.response?.data?.detail || 'Не удалось загрузить' }
  }
})
async function submit(){
  loading.value=true
  error.value=''
  if (!form.name || !form.name.trim()) { error.value='Название обязательно'; loading.value=false; return }
  if (!form.product_id) { error.value='Выберите услугу'; loading.value=false; return }
  if (form.budget == null || isNaN(form.budget) || Number(form.budget) < 0) { error.value='Бюджет должен быть >=0'; loading.value=false; return }
  const payload = { name: form.name.trim(), product_id: Number(form.product_id), promotion_channel: form.promotion_channel.trim(), budget: Number(form.budget) }
  try{
    if(isEdit.value) await client.put(`/ads/${route.params.id}`, payload)
    else await client.post('/ads', payload)
    router.push('/ads')
  }catch(e){
    const data=e.response?.data
    if (Array.isArray(data?.detail)) error.value=data.detail.map(d=>d.msg).join(', ')
    else error.value=data?.detail || JSON.stringify(data) || 'Ошибка'
  }finally{loading.value=false}
}
</script>
