import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import { BookOpen, User, Calendar, CheckCircle, XCircle, ArrowLeft } from 'lucide-react'

export default function BookDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
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
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.book?.[0] || 
                          error.response?.data?.non_field_errors?.[0] ||
                          'Failed to checkout book'
      setMessage({
        type: 'error',
        text: errorMessage
      })
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

      {message.text && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success'
            ? 'bg-green-50 border border-green-200 text-green-700'
            : 'bg-red-50 border border-red-200 text-red-700'
        }`}>
          {message.text}
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
            
            {book.copies_available > 0 ? (
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

