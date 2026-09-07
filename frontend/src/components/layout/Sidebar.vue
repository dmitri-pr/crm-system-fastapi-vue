<template>
  <div class="sidebar" id="side_nav">
    <div class="header-box px-3 pt-4 pb-4">
      <h1 class="fs-4 nav-logo text-center">
        <span class="text-black text-uppercase fw-bold">
          <router-link class="link-dark text-decoration-none" to="/">CRM BACKOFFICE</router-link>
        </span>
      </h1>
      <div v-if="auth.user" class="text-center small text-muted mt-2">
        {{ auth.user.username }} ({{ auth.user.role }})
      </div>
    </div>
    <ul class="list-unstyled px-2">
      <li>
        <router-link to="/products" class="bar-item text-decoration-none px-3 py-2 d-block" active-class="active">
          <i class="fas fa-microchip"></i> <span class="ms-1">Услуги</span>
        </router-link>
      </li>
      <li>
        <router-link to="/ads" class="bar-item text-decoration-none px-3 py-2 d-block" active-class="active">
          <i class="fas fa-ad"></i> <span class="ms-1">Рекламные кампании</span>
        </router-link>
      </li>
      <li>
        <router-link to="/leads" class="bar-item text-decoration-none px-3 py-2 d-block" active-class="active">
          <i class="fas fa-user-clock"></i> <span class="ms-1">Лиды</span>
        </router-link>
      </li>
      <li>
        <router-link to="/contracts" class="bar-item text-decoration-none px-3 py-2 d-block" active-class="active">
          <i class="fas fa-file-alt"></i> <span class="ms-1">Контракты</span>
        </router-link>
      </li>
      <li>
        <router-link to="/customers" class="bar-item text-decoration-none px-3 py-2 d-block" active-class="active">
          <i class="fas fa-user-check"></i> <span class="ms-1">Активные клиенты</span>
        </router-link>
      </li>
      <li v-if="auth.isAdmin">
        <router-link to="/users" class="bar-item text-decoration-none px-3 py-2 d-block" active-class="active">
          <i class="fas fa-users"></i> <span class="ms-1">Пользователи</span>
        </router-link>
      </li>
      <li><hr /></li>
      <li>
        <a href="#" @click.prevent="logout" class="bar-item text-decoration-none px-3 py-3 d-block">
          <i class="fas fa-sign-out-alt"></i> <span class="px-1">Выход</span>
        </a>
      </li>
    </ul>
    <div class="px-3 small text-muted">
      <div class="border-top pt-2">
        <strong>Роли:</strong><br/>
        admin — всё<br/>
        operator — лиды<br/>
        marketer — услуги/реклама<br/>
        manager — контракты/клиенты
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
