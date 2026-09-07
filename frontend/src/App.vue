<template>
  <div v-if="$route.path === '/login'">
    <router-view />
  </div>
  <div v-else class="main-container d-flex">
    <Sidebar />
    <div class="content px-3 pt-4">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/layout/Sidebar.vue'
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
onMounted(async () => {
  if (auth.token && !auth.user) {
    try { await auth.fetchMe() } catch(e) { auth.logout() }
  }
})
</script>
