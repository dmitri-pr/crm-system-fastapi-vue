import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'

// Products
import ProductsList from '../views/products/ProductsList.vue'
import ProductDetail from '../views/products/ProductDetail.vue'
import ProductForm from '../views/products/ProductForm.vue'

// Ads
import AdsList from '../views/ads/AdsList.vue'
import AdDetail from '../views/ads/AdDetail.vue'
import AdForm from '../views/ads/AdForm.vue'
import AdStatistics from '../views/ads/AdStatistics.vue'

// Leads
import LeadsList from '../views/leads/LeadsList.vue'
import LeadDetail from '../views/leads/LeadDetail.vue'
import LeadForm from '../views/leads/LeadForm.vue'

// Contracts
import ContractsList from '../views/contracts/ContractsList.vue'
import ContractDetail from '../views/contracts/ContractDetail.vue'
import ContractForm from '../views/contracts/ContractForm.vue'

// Customers
import CustomersList from '../views/customers/CustomersList.vue'
import CustomerDetail from '../views/customers/CustomerDetail.vue'
import CustomerForm from '../views/customers/CustomerForm.vue'

// Users
import UsersList from '../views/users/UsersList.vue'
import UserForm from '../views/users/UserForm.vue'

const routes = [
  { path: '/login', component: LoginView, meta: { public: true } },
  { path: '/', component: DashboardView, meta: { auth: true } },

  { path: '/products', component: ProductsList, meta: { auth: true } },
  { path: '/products/new', component: ProductForm, meta: { auth: true } },
  { path: '/products/:id', component: ProductDetail, meta: { auth: true } },
  { path: '/products/:id/edit', component: ProductForm, meta: { auth: true } },

  { path: '/ads', component: AdsList, meta: { auth: true } },
  { path: '/ads/statistic', component: AdStatistics, meta: { auth: true } },
  { path: '/ads/new', component: AdForm, meta: { auth: true } },
  { path: '/ads/:id', component: AdDetail, meta: { auth: true } },
  { path: '/ads/:id/edit', component: AdForm, meta: { auth: true } },

  { path: '/leads', component: LeadsList, meta: { auth: true } },
  { path: '/leads/new', component: LeadForm, meta: { auth: true } },
  { path: '/leads/:id', component: LeadDetail, meta: { auth: true } },
  { path: '/leads/:id/edit', component: LeadForm, meta: { auth: true } },

  { path: '/contracts', component: ContractsList, meta: { auth: true } },
  { path: '/contracts/new', component: ContractForm, meta: { auth: true } },
  { path: '/contracts/:id', component: ContractDetail, meta: { auth: true } },
  { path: '/contracts/:id/edit', component: ContractForm, meta: { auth: true } },

  { path: '/customers', component: CustomersList, meta: { auth: true } },
  { path: '/customers/new', component: CustomerForm, meta: { auth: true } },
  { path: '/customers/:id', component: CustomerDetail, meta: { auth: true } },
  { path: '/customers/:id/edit', component: CustomerForm, meta: { auth: true } },

  { path: '/users', component: UsersList, meta: { auth: true, adminOnly: true } },
  { path: '/users/new', component: UserForm, meta: { auth: true, adminOnly: true } },
  { path: '/users/:id/edit', component: UserForm, meta: { auth: true, adminOnly: true } },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.isAuthenticated && to.path === '/login') return next('/')
    return next()
  }
  if (to.meta.auth && !auth.isAuthenticated) {
    return next('/login')
  }
  if (to.meta.adminOnly && !auth.isAdmin) {
    return next('/')
  }
  next()
})

export default router
