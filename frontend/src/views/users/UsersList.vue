<template>
  <div>
    <h2 class="fw-bold">Пользователи</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="hstack gap-3 pb-4">
        <router-link to="/users/new" class="btn btn-success">Создать пользователя</router-link>
      </div>
      <div class="col">
        <div v-if="loading" class="text-center">Загрузка...</div>
        <table v-else class="table table-striped">
          <thead>
            <tr><th>ID</th><th>Имя</th><th>Email</th><th>Роль</th><th>Активен</th><th>Действия</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.id }}</td>
              <td>{{ u.username }}<br/><small>{{ u.full_name }}</small></td>
              <td>{{ u.email }}</td>
              <td><span class="badge bg-primary">{{ u.role }}</span></td>
              <td>{{ u.is_active ? 'Да' : 'Нет' }}</td>
              <td>
                <router-link :to="`/users/${u.id}/edit`" class="btn btn-sm btn-primary me-1">Ред.</router-link>
                <button @click="remove(u.id)" class="btn btn-sm btn-danger">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../../api/client'
const users=ref([])
const loading=ref(true)
const error=ref('')
async function load(){
  loading.value=true
  try{ const res=await client.get('/users'); users.value=res.data }catch(e){ error.value = e.response?.data?.detail || 'Ошибка загрузки'; console.error(e); if(e.response?.status===403) alert('Только админ')}
  finally{loading.value=false}
}
async function remove(id){
  if(!confirm('Удалить пользователя?')) return
  try{ await client.delete(`/users/${id}`); users.value=users.value.filter(u=>u.id!==id)}catch(e){ alert(e.response?.data?.detail||'Ошибка')}
}
onMounted(load)
</script>
