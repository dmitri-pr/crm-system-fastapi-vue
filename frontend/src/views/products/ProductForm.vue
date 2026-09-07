<template>
  <div>
    <h2 class="fw-bold">{{ isEdit ? 'Редактирование услуги' : 'Создание услуги' }}</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Название</label>
            <input v-model="form.name" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Описание</label>
            <textarea v-model="form.description" class="form-control" rows="3"></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Стоимость (руб)</label>
            <input v-model.number="form.cost" type="number" step="0.01" class="form-control" required />
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Сохранение...' : (isEdit ? 'Применить' : 'Создать') }}</button>
          <router-link to="/products" class="btn btn-secondary ms-2">Назад</router-link>
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

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const error = ref('')
const form = reactive({ name: '', description: '', cost: 0 })

onMounted(async () => {
  if (isEdit.value) {
    try {
      const res = await client.get(`/products/${route.params.id}`)
      form.name = res.data.name || ''
      form.description = res.data.description || ''
      form.cost = res.data.cost ?? 0
    } catch(e){ error.value = e.response?.data?.detail || 'Не удалось загрузить' }
  }
})

async function submit(){
  loading.value = true
  error.value = ''
  if (!form.name || !form.name.trim()) { error.value = 'Название обязательно'; loading.value=false; return }
  if (form.cost == null || isNaN(form.cost) || Number(form.cost) < 0) { error.value = 'Стоимость должна быть >=0'; loading.value=false; return }
  const payload = { name: form.name.trim(), description: form.description || null, cost: Number(form.cost) }
  try {
    if (isEdit.value) {
      await client.put(`/products/${route.params.id}`, payload)
    } else {
      await client.post('/products', payload)
    }
    router.push('/products')
  } catch(e){
    const data = e.response?.data
    if (Array.isArray(data?.detail)) error.value = data.detail.map(d=> d.msg).join(', ')
    else error.value = data?.detail || JSON.stringify(data) || 'Ошибка'
  } finally { loading.value=false }
}
</script>
