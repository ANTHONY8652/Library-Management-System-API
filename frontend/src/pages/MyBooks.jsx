import { useEffect, useState } from 'react'
import api from '../services/api'
import { BookOpen, Calendar, AlertCircle, CheckCircle } from 'lucide-react'

export default function MyBooks() {
  const [transactions, setTransactions] = useState([])
  const [overdueBooks, setOverdueBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [returning, setReturning] = useState(null)

  useEffect(() => {
    fetchMyBooks()
    fetchOverdueBooks()
  }, [])

  const fetchMyBooks = async () => {
    try {
      // Fetch all currently borrowed books (not returned) for the user
      const response = await api.get('/my-books/')
      // Handle both paginated and non-paginated responses
      const data = response.data.results || response.data
      setTransactions(data.filter(t => !t.return_date))
    } catch (error) {
      console.error('Error fetching my books:', error)
      // If error, just set empty array
      setTransactions([])
    }
  }

  const fetchOverdueBooks = async () => {
    try {
      const response = await api.get('/overdue-books/')
      // Handle both paginated and non-paginated responses
      const data = response.data.results || response.data
      setOverdueBooks(data)
    } catch (error) {
      console.error('Error fetching overdue books:', error)
      setOverdueBooks([])
    } finally {
      setLoading(false)
    }
  }

  const handleReturn = async (transactionId) => {
    setReturning(transactionId)
    try {
      await api.patch(`/return/${transactionId}/`, {
        return_date: new Date().toISOString().split('T')[0]
      })
      // Refresh both lists
      await Promise.all([fetchMyBooks(), fetchOverdueBooks()])
    } catch (error) {
      console.error('Error returning book:', error)
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail || 
                          'Failed to return book. Please try again.'
      alert(errorMessage)
    } finally {
      setReturning(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Books</h1>
        <p className="mt-2 text-gray-600">Manage your borrowed books</p>
      </div>

      {overdueBooks.length > 0 && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center mb-4">
            <AlertCircle className="h-6 w-6 text-red-600 mr-2" />
            <h2 className="text-xl font-semibold text-red-900">Overdue Books</h2>
          </div>
          <div className="space-y-4">
            {overdueBooks.map((transaction) => (
              <div key={transaction.id} className="bg-white p-4 rounded-lg border border-red-200">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{transaction.book?.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">by {transaction.book?.author}</p>
                    <div className="mt-2 text-sm text-red-600">
                      <p>Due: {new Date(transaction.due_date).toLocaleDateString()}</p>
                      {transaction.overdue_penalty > 0 && (
                        <p className="font-medium">Penalty: ${transaction.overdue_penalty}</p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleReturn(transaction.id)}
                    disabled={returning === transaction.id}
                    className="btn-primary ml-4"
                  >
                    {returning === transaction.id ? 'Returning...' : 'Return'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Currently Borrowed</h2>
        {transactions.length === 0 && overdueBooks.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">You don't have any borrowed books</p>
          </div>
        ) : (
          <div className="space-y-4">
            {transactions
              .filter(t => !overdueBooks.some(ob => ob.id === t.id)) // Don't show overdue books twice
              .map((transaction) => (
                <div key={transaction.id} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{transaction.book?.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">by {transaction.book?.author}</p>
                      <div className="mt-2 text-sm text-gray-600">
                        <p>Checked out: {new Date(transaction.checkout_date).toLocaleDateString()}</p>
                        <p>Due: {new Date(transaction.due_date).toLocaleDateString()}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleReturn(transaction.id)}
                      disabled={returning === transaction.id}
                      className="btn-primary ml-4"
                    >
                      {returning === transaction.id ? 'Returning...' : 'Return'}
                    </button>
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  )
}

