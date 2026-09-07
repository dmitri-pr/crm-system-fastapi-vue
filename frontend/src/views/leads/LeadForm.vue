<template>
  <div>
    <h2 class="fw-bold">{{ isEdit ? 'Редактирование лида' : 'Создание лида' }}</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Фамилия</label>
            <input v-model="form.last_name" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Имя</label>
            <input v-model="form.first_name" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Отчество</label>
            <input v-model="form.patronymic" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Телефон</label>
            <input v-model="form.phone" class="form-control" required placeholder="+7 999 123-45-67" />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Рекламная кампания</label>
            <select v-model.number="form.advertisement_id" class="form-select">
              <option :value="null">— Не выбрано —</option>
              <option v-for="ad in ads" :key="ad.id" :value="ad.id">{{ ad.name }}</option>
            </select>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '...' : (isEdit ? 'Применить' : 'Создать') }}</button>
          <router-link to="/leads" class="btn btn-secondary ms-2">Назад</router-link>
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
const ads=ref([])
const form=reactive({ last_name:'', first_name:'', patronymic:'', phone:'', email:'', advertisement_id: null })

onMounted(async()=>{
  try{
    const res=await client.get('/ads')
    ads.value=res.data
  }catch(e){ error.value = 'Не удалось загрузить кампании'; console.error(e)}
  if(isEdit.value){
    try{
      const res=await client.get(`/leads/${route.params.id}`)
      form.last_name = res.data.last_name || ''
      form.first_name = res.data.first_name || ''
      form.patronymic = res.data.patronymic || ''
      form.phone = res.data.phone || ''
      form.email = res.data.email || ''
      form.advertisement_id = res.data.advertisement_id ?? null
    }catch(e){ error.value = e.response?.data?.detail || 'Не удалось загрузить' }
  }
})
async function submit(){
  loading.value=true
  error.value=''
  if (!form.last_name || !form.last_name.trim()) { error.value='Фамилия обязательна'; loading.value=false; return }
  if (!form.first_name || !form.first_name.trim()) { error.value='Имя обязательно'; loading.value=false; return }
  if (!form.phone || !form.phone.trim()) { error.value='Телефон обязателен'; loading.value=false; return }
  if (!form.email || !form.email.trim()) { error.value='Email обязателен'; loading.value=false; return }
  const payload={
    last_name: form.last_name.trim(),
    first_name: form.first_name.trim(),
    patronymic: form.patronymic ? form.patronymic.trim() : null,
    phone: form.phone.trim(),
    email: form.email.trim(),
    advertisement_id: form.advertisement_id ? Number(form.advertisement_id) : null
  }
  try{
    if(isEdit.value) await client.put(`/leads/${route.params.id}`, payload)
    else await client.post('/leads', payload)
    router.push('/leads')
  }catch(e){
    const data=e.response?.data
    if (Array.isArray(data?.detail)) error.value=data.detail.map(d=>d.msg).join(', ')
    else error.value=data?.detail || JSON.stringify(data) || 'Ошибка'
  }
  finally{loading.value=false}
}
</script>
