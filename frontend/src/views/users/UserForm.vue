<template>
  <div>
    <h2 class="fw-bold">{{ isEdit ? 'Редактирование пользователя' : 'Создание пользователя' }}</h2>
    <div class="row bg-white px-3 py-3 mx-2 my-5 rounded pb-5 shadow-lg">
      <div class="col"></div>
      <div class="col">
        <form @submit.prevent="submit">
          <div class="mb-3" v-if="!isEdit">
            <label class="form-label">Имя пользователя</label>
            <input v-model="form.username" class="form-control" required />
          </div>
          <div v-else class="mb-3">
            <label class="form-label">Имя пользователя</label>
            <input :value="form.username" class="form-control" disabled />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">ФИО</label>
            <input v-model="form.full_name" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Роль</label>
            <select v-model="form.role" class="form-select" required>
              <option value="admin">admin - Администратор</option>
              <option value="operator">operator - Оператор</option>
              <option value="marketer">marketer - Маркетолог</option>
              <option value="manager">manager - Менеджер</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">{{ isEdit ? 'Новый пароль (оставьте пустым чтобы не менять)' : 'Пароль' }}</label>
            <input v-model="form.password" type="password" class="form-control" :required="!isEdit" />
          </div>
          <div class="mb-3 form-check">
            <input v-model="form.is_active" type="checkbox" class="form-check-input" id="activeCheck" />
            <label class="form-check-label" for="activeCheck">Активен</label>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '...' : (isEdit ? 'Применить' : 'Создать') }}</button>
          <router-link to="/users" class="btn btn-secondary ms-2">Назад</router-link>
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
const form=reactive({ username:'', email:'', full_name:'', role:'manager', password:'', is_active:true })

onMounted(async()=>{
  if(isEdit.value){
    try{
      const res=await client.get(`/users/${route.params.id}`)
      form.username=res.data.username
      form.email=res.data.email
      form.full_name=res.data.full_name || ''
      form.role=res.data.role
      form.is_active=res.data.is_active
      form.password=''
    }catch(e){ error.value='Не удалось загрузить' }
  }
})
async function submit(){
  loading.value=true
  error.value=''
  if (!isEdit.value && (!form.username || form.username.trim().length < 3)) { error.value='Имя пользователя минимум 3 символа'; loading.value=false; return }
  if (!form.email || !form.email.trim()) { error.value='Email обязателен'; loading.value=false; return }
  if (!isEdit.value && (!form.password || form.password.length < 8)) { error.value='Пароль минимум 8 символов'; loading.value=false; return }
  if (isEdit.value && form.password && form.password.length < 8) { error.value='Пароль минимум 8 символов'; loading.value=false; return }
  try{
    if(isEdit.value){
      const payload={ email: form.email.trim(), full_name: form.full_name ? form.full_name.trim() : null, role: form.role, is_active: form.is_active }
      if(form.password) payload.password=form.password
      await client.put(`/users/${route.params.id}`, payload)
    } else {
      await client.post('/users', { username: form.username.trim(), email: form.email.trim(), full_name: form.full_name ? form.full_name.trim() : null, role: form.role, password: form.password, is_active: form.is_active })
    }
    router.push('/users')
  }catch(e){
    const data=e.response?.data
    if (Array.isArray(data?.detail)) error.value=data.detail.map(d=>d.msg).join(', ')
    else error.value=data?.detail || JSON.stringify(data) || 'Ошибка'
  }finally{loading.value=false}
}
</script>
