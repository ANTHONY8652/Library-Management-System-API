import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { BookOpen, Mail, ArrowLeft, UserPlus, AlertCircle } from 'lucide-react'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showSignupPrompt, setShowSignupPrompt] = useState(false)
  const [loading, setLoading] = useState(false)
  const { requestPasswordReset } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setShowSignupPrompt(false)
    setLoading(true)

    const result = await requestPasswordReset(email)
    
    if (result.success) {
      // Check if email doesn't exist
      if (result.email_exists === false || result.suggest_signup) {
        setShowSignupPrompt(true)
        setSuccess(result.message || 'No account found with this email address.')
      } else {
        // Email exists and reset link was sent
        const message = result.message || 'Password reset link has been sent to your email address.'
        setSuccess(message)
        setEmail('')
        
        // If message mentions console, make it more prominent
        if (message.includes('console') || message.includes('terminal')) {
          setSuccess(message + ' Please check the terminal/console where your Django server is running.')
        }
      }
    } else {
      setError(result.error || 'Error sending password reset email. Please try again.')
    }
    
    setLoading(false)
  }

  const handleGoToSignup = () => {
    navigate('/register')
  }

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
            Enter your email address and we'll send you a link to reset your password.
          </p>
        </div>
        
        <div className="card">
          <form className="space-y-6" onSubmit={handleSubmit}>
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
                <div className="flex items-start">
                  <AlertCircle className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="font-medium mb-2">{success}</p>
                    <p className="text-sm mb-3">
                      It looks like you don't have an account yet. Would you like to create one?
                    </p>
                    <button
                      type="button"
                      onClick={handleGoToSignup}
                      className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                    >
                      <UserPlus className="h-4 w-4 mr-2" />
                      Create Account
                    </button>
                  </div>
                </div>
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
                  // Clear signup prompt when user starts typing
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
                    Send Reset Link
                  </>
                )}
              </button>
            </div>

            <div className="text-center space-y-2">
              <Link 
                to="/login"
                className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to Login
              </Link>
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link 
                  to="/register" 
                  className="font-medium text-primary-600 hover:text-primary-500"
                >
                  Sign up
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

