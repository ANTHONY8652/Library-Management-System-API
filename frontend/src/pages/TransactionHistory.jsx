import { useEffect, useState } from 'react'
import api from '../services/api'
import { History, BookOpen, Calendar, CheckCircle, Clock } from 'lucide-react'

export default function TransactionHistory() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, current, returned

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await api.get('/transaction-history/')
      const data = response.data.results || response.data
      setTransactions(data)
    } catch (error) {
      console.error('Error fetching transaction history:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredTransactions = transactions.filter(t => {
    if (filter === 'current') return !t.return_date
    if (filter === 'returned') return t.return_date
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Transaction History</h1>
          <p className="mt-2 text-gray-600">View all your book transactions</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === 'all' ? 'btn-primary' : 'btn-secondary'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('current')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === 'current' ? 'btn-primary' : 'btn-secondary'
            }`}
          >
            Current
          </button>
          <button
            onClick={() => setFilter('returned')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              filter === 'returned' ? 'btn-primary' : 'btn-secondary'
            }`}
          >
            Returned
          </button>
        </div>
      </div>

      {filteredTransactions.length === 0 ? (
        <div className="card text-center py-12">
          <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No transactions found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTransactions.map((transaction) => (
            <div
              key={transaction.id}
              className={`card ${
                transaction.return_date 
                  ? 'bg-gray-50' 
                  : transaction.due_date && new Date(transaction.due_date) < new Date()
                  ? 'bg-red-50 border-red-200'
                  : ''
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <BookOpen className="h-5 w-5 text-primary-600" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      {transaction.book?.title}
                    </h3>
                    {transaction.return_date ? (
                      <span className="flex items-center text-sm text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Returned
                      </span>
                    ) : (
                      <span className="flex items-center text-sm text-blue-600">
                        <Clock className="h-4 w-4 mr-1" />
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">by {transaction.book?.author}</p>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Checked Out:</span>
                      <p className="font-medium text-gray-900">
                        {new Date(transaction.checkout_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Due Date:</span>
                      <p className="font-medium text-gray-900">
                        {transaction.due_date ? new Date(transaction.due_date).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                    {transaction.return_date && (
                      <div>
                        <span className="text-gray-500">Returned:</span>
                        <p className="font-medium text-gray-900">
                          {new Date(transaction.return_date).toLocaleDateString()}
                        </p>
                      </div>
                    )}
                    {transaction.overdue_penalty > 0 && (
                      <div>
                        <span className="text-gray-500">Penalty:</span>
                        <p className="font-medium text-red-600">
                          ${transaction.overdue_penalty.toFixed(2)}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

