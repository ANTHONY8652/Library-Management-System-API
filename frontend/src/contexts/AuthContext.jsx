import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData))
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } catch (error) {
        console.error('Error parsing user data:', error)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    try {
      const response = await api.post('/login/', { username, password })
      const { access, refresh, ...userData } = response.data
      
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))
      
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error.response?.data)
      // Handle different error response formats from DRF
      let errorMessage = 'Invalid credentials'
      if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = Array.isArray(error.response.data.error) 
            ? error.response.data.error[0] 
            : error.response.data.error
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail
        } else if (error.response.data.non_field_errors) {
          errorMessage = Array.isArray(error.response.data.non_field_errors)
            ? error.response.data.non_field_errors[0]
            : error.response.data.non_field_errors
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data
        }
      }
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  const register = async (username, email, password) => {
    try {
      const response = await api.post('/register/', { username, email, password })
      const { access, refresh, ...userData } = response.data
      
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      localStorage.setItem('user', JSON.stringify(userData))
      
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      let errorMessage = 'Registration failed'
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error
        } else if (error.response.data.username) {
          errorMessage = `Username: ${Array.isArray(error.response.data.username) ? error.response.data.username[0] : error.response.data.username}`
        } else if (error.response.data.email) {
          errorMessage = `Email: ${Array.isArray(error.response.data.email) ? error.response.data.email[0] : error.response.data.email}`
        } else if (error.response.data.password) {
          errorMessage = `Password: ${Array.isArray(error.response.data.password) ? error.response.data.password[0] : error.response.data.password}`
        } else {
          errorMessage = JSON.stringify(error.response.data)
        }
      }
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  const logout = async () => {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        await api.post('/logout/', { refresh })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

