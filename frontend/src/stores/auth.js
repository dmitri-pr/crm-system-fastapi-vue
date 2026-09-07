import { defineStore } from 'pinia'
import client from '../api/client'

function safeParseUser() {
  try {
    const raw = localStorage.getItem('user')
    if (!raw || raw === 'null' || raw === 'undefined') return null
    return JSON.parse(raw)
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: safeParseUser(),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    role: (state) => (state.user ? state.user.role : null),
    isAdmin: (state) => state.user && (state.user.role === 'admin' || state.user.is_superuser),
    canManageProducts: (state) => {
      if (!state.user) return false
      return ['admin', 'marketer'].includes(state.user.role) || state.user.is_superuser
    },
    canManageAds: (state) => {
      if (!state.user) return false
      return ['admin', 'marketer'].includes(state.user.role) || state.user.is_superuser
    },
    canManageLeads: (state) => {
      if (!state.user) return false
      return ['admin', 'operator'].includes(state.user.role) || state.user.is_superuser
    },
    canManageContracts: (state) => {
      if (!state.user) return false
      return ['admin', 'manager'].includes(state.user.role) || state.user.is_superuser
    },
    canManageCustomers: (state) => {
      if (!state.user) return false
      return ['admin', 'manager'].includes(state.user.role) || state.user.is_superuser
    },
  },
  actions: {
    async login(username, password) {
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)
      const res = await client.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      const token = res.data.access_token
      this.token = token
      localStorage.setItem('access_token', token)
      await this.fetchMe()
      return res
    },
    async fetchMe() {
      try {
        const res = await client.get('/auth/me')
        this.user = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
      } catch (e) {
        // Не разлогиниваем при 500, только при 401
        if (e.response && e.response.status === 401) {
          this.logout()
        }
        throw e
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    },
  },
})
