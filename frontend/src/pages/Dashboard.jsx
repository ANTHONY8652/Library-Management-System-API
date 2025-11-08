import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { BookOpen, Clock, TrendingUp, AlertCircle } from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalBooks: 0,
    availableBooks: 0,
    myBooks: 0,
    overdueBooks: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const [booksRes, availableRes, myBooksRes, overdueRes] = await Promise.all([
        api.get('/books/').catch(() => ({ data: [] })),
        api.get('/available-books/').catch(() => ({ data: [] })),
        api.get('/my-books/').catch(() => ({ data: [] })),
        api.get('/overdue-books/').catch(() => ({ data: [] }))
      ])

      // Handle paginated responses
      const totalBooks = booksRes.data.count || (Array.isArray(booksRes.data) ? booksRes.data.length : 0)
      const availableBooks = availableRes.data.count || (Array.isArray(availableRes.data) ? availableRes.data.length : (Array.isArray(availableRes.data.results) ? availableRes.data.results.length : 0))
      const myBooks = myBooksRes.data.results ? myBooksRes.data.results.length : (Array.isArray(myBooksRes.data) ? myBooksRes.data.length : 0)
      const overdueBooks = overdueRes.data.results ? overdueRes.data.results.length : (Array.isArray(overdueRes.data) ? overdueRes.data.length : 0)

      setStats({
        totalBooks,
        availableBooks,
        myBooks,
        overdueBooks
      })
    } catch (error) {
      console.error('Error fetching stats:', error)
      // Set default values on error
      setStats({
        totalBooks: 0,
        availableBooks: 0,
        myBooks: 0,
        overdueBooks: 0
      })
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    {
      title: 'Total Books',
      value: stats.totalBooks,
      icon: BookOpen,
      color: 'bg-blue-500',
      link: '/books'
    },
    {
      title: 'Available Books',
      value: stats.availableBooks,
      icon: TrendingUp,
      color: 'bg-green-500',
      link: '/books'
    },
    {
      title: 'My Books',
      value: stats.myBooks,
      icon: Clock,
      color: 'bg-purple-500',
      link: '/my-books'
    },
    {
      title: 'Overdue',
      value: stats.overdueBooks,
      icon: AlertCircle,
      color: 'bg-red-500',
      link: '/my-books'
    }
  ]

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
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Welcome to your library management system</p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Link
              key={index}
              to={stat.link}
              className="card hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex items-center">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/books"
              className="block w-full btn-primary text-center"
            >
              Browse All Books
            </Link>
            <Link
              to="/my-books"
              className="block w-full btn-secondary text-center"
            >
              View My Books
            </Link>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Library Information</h2>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• Browse our extensive collection of books</p>
            <p>• Check out books for up to 14 days</p>
            <p>• Return books on time to avoid penalties</p>
            <p>• Track your reading history</p>
          </div>
        </div>
      </div>
    </div>
  )
}

