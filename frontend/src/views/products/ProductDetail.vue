<template>
  <div>
    <h2 class="fw-bold">Детальная информация об услуге</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <div v-else-if="product" class="card border-dark shadow" style="background: #eee">
          <div class="card-body">
            <h5 class="card-title fw-bold">{{ product.name }}</h5>
            <p class="card-text">{{ product.description }}</p>
            <div class="d-flex justify-content-end fw-bold">{{ product.cost }} руб</div>
            <div class="d-flex justify-content-center fw-bold gap-2 mt-3">
              <router-link :to="`/products/${product.id}/edit`" class="btn btn-primary">Редактировать</router-link>
              <button @click="remove" class="btn btn-danger">Удалить</button>
            </div>
          </div>
        </div>
        <div v-else class="alert alert-danger">Не найдено</div>
      </div>
      <div class="col"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../../api/client'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await client.get(`/products/${route.params.id}`)
    product.value = res.data
  } catch(e){ error.value = e.response?.data?.detail || 'Не удалось загрузить'; console.error(e) }
  finally{ loading.value=false }
})

async function remove(){
  if(!confirm(`Удалить "${product.value.name}"?`)) return
  try {
    await client.delete(`/products/${product.value.id}`)
    router.push('/products')
  } catch(e){ alert(e.response?.data?.detail || 'Ошибка') }
}
</script>
