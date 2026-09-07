import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  // Не ставим Content-Type глобально, чтобы multipart работал с boundary
  // axios сам выставит application/json для JSON-запросов
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      // Используем history API вместо полной перезагрузки
      if (window.location.pathname !== '/login') {
        // Импортировать router нельзя из-за цикла, используем window.history
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default client
