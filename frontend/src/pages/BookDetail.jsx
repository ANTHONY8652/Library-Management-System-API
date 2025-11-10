import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { BookOpen, User, Calendar, CheckCircle, XCircle, ArrowLeft, LogIn } from 'lucide-react'

export default function BookDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [book, setBook] = useState(null)
  const [loading, setLoading] = useState(true)
  const [checkingOut, setCheckingOut] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchBook()
  }, [id])

  const fetchBook = async () => {
    try {
      setLoading(true)
      setMessage({ type: '', text: '' })
      const response = await api.get(`/books/${id}/`)
      setBook(response.data)
    } catch (error) {
      console.error('Error fetching book:', error)
      const errorMessage = error.response?.status === 404 
        ? 'Book not found' 
        : error.response?.data?.detail || 'Failed to load book details'
      setMessage({ type: 'error', text: errorMessage })
      setBook(null)
    } finally {
      setLoading(false)
    }
  }

  const handleCheckout = async () => {
    // Prevent checkout if user is not authenticated
    if (!user) {
      setMessage({ 
        type: 'error', 
        text: 'You must be signed in to checkout books. Please login or create an account.' 
      })
      // Scroll to top to show the message
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return
    }

    if (!book || book.copies_available <= 0) {
      setMessage({ type: 'error', text: 'This book is not available for checkout' })
      return
    }

    setCheckingOut(true)
    setMessage({ type: '', text: '' })

    try {
      const today = new Date().toISOString().split('T')[0]
      await api.post('/checkout/', {
        book: book.id,
        checkout_date: today
      })
      
      setMessage({ type: 'success', text: 'Book checked out successfully!' })
      setTimeout(() => {
        fetchBook()
        navigate('/my-books')
      }, 1500)
    } catch (error) {
      // Handle authentication errors specifically
      if (error.response?.status === 401) {
        setMessage({
          type: 'error',
          text: 'You must be signed in to checkout books. Please login or create an account.'
        })
      } else {
        const errorMessage = error.response?.data?.error || 
                            error.response?.data?.book?.[0] || 
                            error.response?.data?.non_field_errors?.[0] ||
                            'Failed to checkout book'
        setMessage({
          type: 'error',
          text: errorMessage
        })
      }
    } finally {
      setCheckingOut(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!book) {
    return (
      <div className="card text-center py-12">
        <XCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
        <p className="text-gray-600">Book not found</p>
        <button onClick={() => navigate('/books')} className="mt-4 btn-secondary">
          Back to Books
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/books')}
        className="flex items-center text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-5 w-5 mr-2" />
        Back to Books
      </button>

      {/* Prominent message for anonymous users */}
      {!user && book && book.copies_available > 0 && (
        <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-lg shadow-sm">
          <div className="flex items-start">
            <LogIn className="h-5 w-5 text-amber-600 mr-3 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-amber-800 mb-1">
                Sign in required to checkout
              </h3>
              <p className="text-sm text-amber-700 mb-3">
                You need to create an account or login to checkout this book. It's free and only takes a minute!
              </p>
              <div className="flex flex-wrap gap-2">
                <Link
                  to={`/register?returnTo=${encodeURIComponent(`/books/${id}`)}`}
                  className="inline-flex items-center px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-md hover:bg-amber-700 transition-colors"
                >
                  Create Free Account
                </Link>
                <Link
                  to={`/login?returnTo=${encodeURIComponent(`/books/${id}`)}`}
                  className="inline-flex items-center px-4 py-2 bg-white text-amber-700 text-sm font-medium rounded-md border border-amber-300 hover:bg-amber-50 transition-colors"
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  Login
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {message.text && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success'
            ? 'bg-green-50 border border-green-200 text-green-700'
            : 'bg-red-50 border border-red-200 text-red-700'
        }`}>
          <div className="flex items-start">
            {message.type === 'error' && (
              <XCircle className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
            )}
            <div className="flex-1">
              {message.text}
              {message.type === 'error' && !user && message.text.includes('signed in') && (
                <div className="mt-3 flex flex-wrap gap-2">
                  <Link
                    to={`/register?returnTo=${encodeURIComponent(`/books/${id}`)}`}
                    className="inline-flex items-center px-3 py-1.5 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 transition-colors"
                  >
                    Sign Up
                  </Link>
                  <Link
                    to={`/login?returnTo=${encodeURIComponent(`/books/${id}`)}`}
                    className="inline-flex items-center px-3 py-1.5 bg-white text-primary-700 text-sm font-medium rounded-md border border-primary-300 hover:bg-primary-50 transition-colors"
                  >
                    Login
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-start justify-between mb-6">
              <div className="bg-primary-100 p-4 rounded-lg">
                <BookOpen className="h-8 w-8 text-primary-600" />
              </div>
              <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                book.copies_available > 0
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {book.copies_available > 0 ? 'Available' : 'Unavailable'}
              </span>
            </div>

            <h1 className="text-3xl font-bold text-gray-900 mb-4">{book.title}</h1>

            <div className="space-y-4">
              <div className="flex items-center text-gray-700">
                <User className="h-5 w-5 mr-3 text-gray-400" />
                <div>
                  <span className="text-sm text-gray-500">Author</span>
                  <p className="font-medium">{book.author}</p>
                </div>
              </div>

              <div className="flex items-center text-gray-700">
                <Calendar className="h-5 w-5 mr-3 text-gray-400" />
                <div>
                  <span className="text-sm text-gray-500">Published Date</span>
                  <p className="font-medium">{new Date(book.published_date).toLocaleDateString()}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <span className="text-sm text-gray-500">ISBN</span>
                <p className="font-mono text-lg">{book.isbn}</p>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <span className="text-sm text-gray-500">Copies Available</span>
                <p className="text-2xl font-bold text-primary-600">{book.copies_available}</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div className="card sticky top-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Actions</h2>
            
            {!user ? (
              <div className="space-y-4">
                <div className="p-6 bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-300 rounded-lg text-center shadow-sm">
                  <div className="bg-amber-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <LogIn className="h-8 w-8 text-amber-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Sign In Required
                  </h3>
                  <p className="text-sm text-gray-700 mb-4">
                    You must be signed in to checkout books from our library. Create a free account or login to continue.
                  </p>
                  <div className="flex flex-col gap-3">
                    <Link
                      to={`/register?returnTo=${encodeURIComponent(`/books/${id}`)}`}
                      className="w-full btn-primary flex items-center justify-center py-3 text-base font-semibold"
                    >
                      Create Free Account
                    </Link>
                    <Link
                      to={`/login?returnTo=${encodeURIComponent(`/books/${id}`)}`}
                      className="w-full btn-secondary flex items-center justify-center py-3 text-base font-medium border-2"
                    >
                      <LogIn className="h-5 w-5 mr-2" />
                      Already have an account? Login
                    </Link>
                  </div>
                  <p className="text-xs text-gray-500 mt-4">
                    Free to join • No credit card required • Instant access
                  </p>
                </div>
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Why sign up?</strong> Browse books, checkout titles, track your reading history, and manage your account all in one place.
                  </p>
                </div>
              </div>
            ) : book.copies_available > 0 ? (
              <button
                onClick={handleCheckout}
                disabled={checkingOut}
                className="w-full btn-primary flex items-center justify-center"
              >
                {checkingOut ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    <CheckCircle className="h-5 w-5 mr-2" />
                    Checkout Book
                  </>
                )}
              </button>
            ) : (
              <div className="p-4 bg-gray-50 rounded-lg text-center">
                <XCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">This book is currently unavailable</p>
              </div>
            )}

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Loan Information</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Loan period: 14 days</li>
                <li>• Late fees apply after due date</li>
                <li>• Maximum 1 copy per book</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

