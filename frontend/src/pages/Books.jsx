import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { Search, BookOpen, User, Calendar } from 'lucide-react'

export default function Books() {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState({
    title: '',
    author: '',
    available: true
  })
  const [pagination, setPagination] = useState({
    current: 1,
    total: 0,
    pageSize: 10
  })

  useEffect(() => {
    fetchBooks()
  }, [filters.title, filters.author, filters.available, pagination.current])

  const fetchBooks = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      
      // Use unified search if we have a search term
      if (filters.title && filters.title.trim()) {
        params.append('search', filters.title.trim())
      }
      
      // Only show available books
      if (filters.available) {
        params.append('available', 'true')
      }
      
      params.append('page', pagination.current)
      
      const response = await api.get(`/available-books/?${params.toString()}`)
      const data = response.data.results || response.data
      setBooks(Array.isArray(data) ? data : [])
      
      // Update pagination if available
      if (response.data.count !== undefined) {
        setPagination(prev => ({
          ...prev,
          total: response.data.count,
          current: response.data.current || prev.current
        }))
      }
    } catch (error) {
      console.error('Error fetching books:', error)
      setBooks([])
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    const trimmedTerm = searchTerm.trim()
    
    if (!trimmedTerm) {
      // Clear search if empty - reset filters and reload all books
      setFilters({
        title: '',
        author: '',
        available: true
      })
      setPagination(prev => ({ ...prev, current: 1 }))
      return
    }
    
    // Reset to page 1 on new search and update filters
    setPagination(prev => ({ ...prev, current: 1 }))
    setFilters({
      title: trimmedTerm, // This will be used as the 'search' parameter
      author: '',
      available: true
    })
  }

  // Clear search when searchTerm is cleared via input
  const handleSearchChange = (e) => {
    const value = e.target.value
    setSearchTerm(value)
    // If user clears the input, clear the search immediately
    if (!value.trim()) {
      setFilters({
        title: '',
        author: '',
        available: true
      })
      setPagination(prev => ({ ...prev, current: 1 }))
    }
  }

  // Use books directly from API response (already filtered server-side)
  const filteredBooks = books

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Browse Books</h1>
        <p className="mt-2 text-gray-600">Discover our collection</p>
      </div>

      <div className="card">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              className="input-field pl-10"
              placeholder="Search by title, author, or ISBN..."
              value={searchTerm}
              onChange={handleSearchChange}
            />
          </div>
          <button type="submit" className="btn-primary">
            Search
          </button>
        </form>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredBooks.length === 0 ? (
        <div className="card text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No books found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBooks.map((book) => (
            <div key={book.id} className="card hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-start justify-between mb-4">
                <div className="bg-primary-100 p-3 rounded-lg">
                  <BookOpen className="h-6 w-6 text-primary-600" />
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  book.copies_available > 0
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {book.copies_available > 0 ? 'Available' : 'Unavailable'}
                </span>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
                {book.title}
              </h3>
              
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center">
                  <User className="h-4 w-4 mr-2" />
                  <span>{book.author}</span>
                </div>
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  <span>{new Date(book.published_date).getFullYear()}</span>
                </div>
                <div>
                  <span className="font-medium">ISBN:</span> {book.isbn}
                </div>
                <div>
                  <span className="font-medium">Copies:</span> {book.copies_available}
                </div>
              </div>
              
              <Link
                to={`/books/${book.id}`}
                className="block w-full btn-primary text-center"
              >
                View Details
              </Link>
            </div>
          ))}
        </div>
      )}

      {pagination.total > pagination.pageSize && (
        <div className="flex justify-center items-center space-x-2 mt-6">
          <button
            onClick={() => setPagination(prev => ({ ...prev, current: Math.max(1, prev.current - 1) }))}
            disabled={pagination.current === 1}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {pagination.current} of {Math.ceil(pagination.total / pagination.pageSize)}
          </span>
          <button
            onClick={() => setPagination(prev => ({ ...prev, current: prev.current + 1 }))}
            disabled={pagination.current >= Math.ceil(pagination.total / pagination.pageSize)}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

