<template>
  <div>
    <h2 class="fw-bold">{{ isEdit ? 'Редактирование активного клиента' : 'Создание активного клиента' }}</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <form @submit.prevent="submit">
          <div class="mb-3" v-if="!isEdit">
            <label class="form-label">Лид (потенциальный клиент)</label>
            <select v-model.number="form.lead_id" class="form-select" required :disabled="!!preselectedLeadId">
              <option :value="null" disabled>Выберите лида</option>
              <option v-for="lead in availableLeads" :key="lead.id" :value="lead.id">
                {{ lead.last_name }} {{ lead.first_name }} — {{ lead.email }} ({{ lead.phone }})
              </option>
            </select>
            <small v-if="preselectedLeadId" class="text-muted">Лид предвыбран из списка (ID={{ preselectedLeadId }})</small>
          </div>
          <div v-else class="mb-3">
            <label class="form-label">Лид</label>
            <input :value="currentLeadName" class="form-control" disabled />
          </div>
          <div class="mb-3">
            <label class="form-label">Контракт</label>
            <select v-model.number="form.contract_id" class="form-select" required>
              <option :value="null" disabled>Выберите контракт</option>
              <option v-for="c in contracts" :key="c.id" :value="c.id">{{ c.name }} — {{ c.product_name }} ({{ c.cost }} руб)</option>
            </select>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '...' : (isEdit ? 'Применить' : 'Создать') }}</button>
          <router-link to="/customers" class="btn btn-secondary ms-2">Назад</router-link>
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
const rawLeadId = route.query.lead_id
const q = rawLeadId ? Number(rawLeadId) : NaN
const preselectedLeadId=ref(Number.isInteger(q) && q > 0 ? q : null)
const loading=ref(false)
const error=ref('')
const availableLeads=ref([])
const contracts=ref([])
const currentLeadName=ref('')
const form=reactive({ lead_id: preselectedLeadId.value, contract_id: null })

onMounted(async()=>{
  try{
    const cRes=await client.get('/contracts')
    contracts.value=cRes.data
  }catch(e){ error.value='Не удалось загрузить контракты'; console.error(e)}
  if(isEdit.value){
    try{
      const res=await client.get(`/customers/${route.params.id}`)
      form.contract_id=res.data.contract_id
      form.lead_id=res.data.lead_id
      currentLeadName.value=res.data.lead ? `${res.data.lead.last_name} ${res.data.lead.first_name}` : `ID ${res.data.lead_id}`
    }catch(e){ error.value= e.response?.data?.detail || 'Не удалось загрузить' }
  } else {
    if(preselectedLeadId.value){
      // load that lead to display, but still need available leads list for validation
      try{
        const lRes=await client.get(`/leads/${preselectedLeadId.value}`)
        if (lRes.data.is_converted) {
          error.value='Этот лид уже конвертирован'
          const aRes=await client.get('/customers/available/leads')
          availableLeads.value=aRes.data
          form.lead_id=null
        } else {
          availableLeads.value=[lRes.data]
          form.lead_id=preselectedLeadId.value
        }
      }catch(e){
        // fallback to available list
        try{
          const aRes=await client.get('/customers/available/leads')
          availableLeads.value=aRes.data
        }catch(e2){ console.error(e2) }
      }
    } else {
      try{
        const aRes=await client.get('/customers/available/leads')
        availableLeads.value=aRes.data
      }catch(e){ console.error(e) }
    }
  }
})

async function submit(){
  loading.value=true
  error.value=''
  if (!isEdit.value && (!form.lead_id || isNaN(form.lead_id))) { error.value='Выберите лида'; loading.value=false; return }
  if (!form.contract_id) { error.value='Выберите контракт'; loading.value=false; return }
  try{
    if(isEdit.value){
      await client.put(`/customers/${route.params.id}`, { contract_id: Number(form.contract_id) })
    } else {
      await client.post('/customers', { lead_id: Number(form.lead_id), contract_id: Number(form.contract_id) })
    }
    router.push('/customers')
  }catch(e){
    const data=e.response?.data
    if (Array.isArray(data?.detail)) error.value=data.detail.map(d=>d.msg).join(', ')
    else error.value=data?.detail || JSON.stringify(data) || 'Ошибка'
  }finally{loading.value=false}
}
</script>
