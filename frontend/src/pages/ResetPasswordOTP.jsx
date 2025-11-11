import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { BookOpen, Lock, CheckCircle, Mail } from 'lucide-react'

export default function ResetPasswordOTP() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1: email, 2: code + password
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [formData, setFormData] = useState({
    new_password: '',
    new_password_confirm: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [showSignupPrompt, setShowSignupPrompt] = useState(false)
  const { requestPasswordReset, verifyOTPAndResetPassword } = useAuth()

  const handleEmailSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setShowSignupPrompt(false)
    
    const trimmedEmail = email.trim()
    if (!trimmedEmail || !trimmedEmail.includes('@')) {
      setError('Please enter a valid email address')
      return
    }
    
    setLoading(true)
    const result = await requestPasswordReset(trimmedEmail)
    
    if (result.success) {
      if (result.email_exists === false || result.suggest_signup) {
        setShowSignupPrompt(true)
        setSuccess(result.message || 'No account found with this email address.')
      } else {
        setSuccess(result.message || 'A 6-digit verification code has been sent to your email address.')
        setStep(2) // Move to code entry step
      }
    } else {
      setError(result.error || 'Error sending verification code. Please try again.')
    }
    
    setLoading(false)
  }

  const handleResetSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (code.length !== 6 || !/^\d+$/.test(code)) {
      setError('Please enter a valid 6-digit code')
      return
    }

    if (formData.new_password !== formData.new_password_confirm) {
      setError('Passwords do not match')
      return
    }

    if (formData.new_password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    setLoading(true)
    const result = await verifyOTPAndResetPassword(
      email.trim(),
      code,
      formData.new_password,
      formData.new_password_confirm
    )
    
    if (result.success) {
      setSuccess('Password reset successful! Redirecting to login...')
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } else {
      setError(result.error || 'Error resetting password. Please try again.')
    }
    
    setLoading(false)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleCodeChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6)
    setCode(value)
    setError('')
  }

  if (step === 1) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="flex justify-center">
              <div className="bg-primary-600 p-3 rounded-full">
                <BookOpen className="h-10 w-10 text-white" />
              </div>
            </div>
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Forgot Password?
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Enter your email address and we'll send you a verification code.
            </p>
          </div>
          
          <div className="card">
            <form className="space-y-6" onSubmit={handleEmailSubmit}>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}
              
              {success && !showSignupPrompt && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
                  {success}
                </div>
              )}

              {showSignupPrompt && (
                <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-4 rounded-lg">
                  <p className="font-medium mb-2">{success}</p>
                  <p className="text-sm mb-3">
                    It looks like you don't have an account yet. Would you like to create one?
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate('/register')}
                    className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700"
                  >
                    Create Account
                  </button>
                </div>
              )}
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="input-field"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (showSignupPrompt) {
                      setShowSignupPrompt(false)
                      setSuccess('')
                    }
                  }}
                  disabled={loading}
                />
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full btn-primary flex items-center justify-center"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Mail className="h-5 w-5 mr-2" />
                      Send Verification Code
                    </>
                  )}
                </button>
              </div>

              <div className="text-center">
                <Link 
                  to="/login"
                  className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  Back to Login
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-primary-600 p-3 rounded-full">
              <Lock className="h-10 w-10 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Reset Your Password
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Enter the 6-digit code sent to <strong>{email}</strong> and your new password.
          </p>
        </div>
        
        <div className="card">
          <form className="space-y-6" onSubmit={handleResetSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
                {success}
              </div>
            )}
            
            <div>
              <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
                Verification Code
              </label>
              <input
                id="code"
                name="code"
                type="text"
                required
                maxLength={6}
                className="input-field text-center text-2xl tracking-widest font-mono"
                placeholder="000000"
                value={code}
                onChange={handleCodeChange}
                disabled={loading}
              />
              <p className="mt-1 text-xs text-gray-500">
                Didn't receive the code? <button type="button" onClick={() => setStep(1)} className="text-primary-600 hover:text-primary-500">Request a new one</button>
              </p>
            </div>

            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <input
                id="new_password"
                name="new_password"
                type="password"
                required
                className="input-field"
                placeholder="Enter new password (min. 8 characters)"
                value={formData.new_password}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="new_password_confirm" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <input
                id="new_password_confirm"
                name="new_password_confirm"
                type="password"
                required
                className="input-field"
                placeholder="Confirm new password"
                value={formData.new_password_confirm}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary flex items-center justify-center"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    <CheckCircle className="h-5 w-5 mr-2" />
                    Reset Password
                  </>
                )}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Use a different email address
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

