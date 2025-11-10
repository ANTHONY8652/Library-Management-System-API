import axios from 'axios'

// Backend API URL - Can be set via environment variable or defaults
// For custom domain: Set VITE_API_URL in Vercel environment variables
// Format: https://api.yourdomain.com/api
const getApiBaseUrl = () => {
  // If VITE_API_URL is set, use it (should include /api)
  if (import.meta.env.VITE_API_URL) {
    const url = import.meta.env.VITE_API_URL.trim()
    // Ensure it ends with /api
    return url.endsWith('/api') ? url : `${url}/api`
  }
  
  // Check if we're in production (Vercel deployment)
  // In production, use custom domain API
  if (import.meta.env.MODE === 'production' || window.location.hostname !== 'localhost') {
    return 'https://api.librarymanagementsystem.store/api'
  }
  
  // Development: use localhost
  return 'http://localhost:8000/api'
}

const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Request interceptor to add auth token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refresh = localStorage.getItem('refresh_token')
        if (refresh) {
          const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
            refresh: refresh,
          })
          const { access } = response.data
          localStorage.setItem('access_token', access)
          api.defaults.headers.common['Authorization'] = `Bearer ${access}`
          originalRequest.headers['Authorization'] = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Only redirect to login if user was authenticated and trying to access protected resource
        // Don't redirect for public endpoints accessed by anonymous users
        const user = localStorage.getItem('user')
        if (user && !originalRequest.url?.includes('/available-books/') && !originalRequest.url?.includes('/books/')) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          // Only redirect if not already on login/register/home page
          if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register') && window.location.pathname !== '/') {
            window.location.href = '/login'
          }
        }
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api

