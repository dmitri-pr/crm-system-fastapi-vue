<template>
  <div>
    <h2 class="fw-bold">{{ isEdit ? 'Редактирование контракта' : 'Создание контракта' }}</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <form @submit.prevent="submit" enctype="multipart/form-data">
          <div class="mb-3">
            <label class="form-label">Название</label>
            <input v-model="form.name" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Услуга</label>
            <select v-model.number="form.product_id" class="form-select" required>
              <option :value="null" disabled>Выберите услугу</option>
              <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Дата заключения</label>
            <input v-model="form.start_date" type="date" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Дата окончания</label>
            <input v-model="form.end_date" type="date" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Сумма (руб)</label>
            <input v-model.number="form.cost" type="number" step="0.01" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Документ (файл)</label>
            <input type="file" @change="onFile" class="form-control" />
            <small v-if="existingDoc" class="text-muted">Текущий файл: <a :href="existingDoc" target="_blank">открыть</a></small>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '...' : (isEdit ? 'Применить' : 'Создать') }}</button>
          <router-link to="/contracts" class="btn btn-secondary ms-2">Назад</router-link>
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
const file=ref(null)
const existingDoc=ref('')
const form=reactive({ name:'', product_id: null, start_date:'', end_date:'', cost:0 })

function onFile(e){ file.value = e.target.files[0] }

onMounted(async()=>{
  try{
    const res=await client.get('/products')
    products.value=res.data
  }catch(e){ error.value='Не удалось загрузить услуги'; console.error(e)}
  if(isEdit.value){
    try{
      const res=await client.get(`/contracts/${route.params.id}`)
      form.name = res.data.name || ''
      form.product_id = res.data.product_id ?? null
      form.start_date = res.data.start_date || ''
      form.end_date = res.data.end_date || ''
      form.cost = res.data.cost ?? 0
      existingDoc.value=res.data.document
    }catch(e){ error.value= e.response?.data?.detail || 'Не удалось загрузить' }
  }
})

async function submit(){
  loading.value=true
  error.value=''
  if (!form.name || !form.name.trim()) { error.value='Название обязательно'; loading.value=false; return }
  if (!form.product_id) { error.value='Выберите услугу'; loading.value=false; return }
  if (!form.start_date) { error.value='Дата начала обязательна'; loading.value=false; return }
  if (!form.end_date) { error.value='Дата окончания обязательна'; loading.value=false; return }
  if (form.start_date && form.end_date && form.start_date > form.end_date) { error.value='Дата начала не может быть позже окончания'; loading.value=false; return }
  if (form.cost == null || isNaN(form.cost) || Number(form.cost) < 0) { error.value='Сумма должна быть >=0'; loading.value=false; return }
  if (file.value && file.value.size > 10*1024*1024) { error.value='Файл слишком большой (макс 10 MB)'; loading.value=false; return }
  try{
    const fd=new FormData()
    fd.append('name', form.name.trim())
    fd.append('product_id', form.product_id)
    fd.append('start_date', form.start_date)
    fd.append('end_date', form.end_date)
    fd.append('cost', form.cost)
    if(file.value) fd.append('document', file.value)
    if(isEdit.value){
      await client.put(`/contracts/${route.params.id}`, fd)
    } else {
      await client.post('/contracts', fd)
    }
    router.push('/contracts')
  }catch(e){
    const data=e.response?.data
    if (Array.isArray(data?.detail)) error.value=data.detail.map(d=>d.msg).join(', ')
    else error.value=data?.detail || JSON.stringify(data) || 'Ошибка'
  }finally{loading.value=false}
}
</script>
