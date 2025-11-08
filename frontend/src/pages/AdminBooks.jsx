import { useEffect, useState } from 'react'
import api from '../services/api'
import { Plus, Edit2, Trash2, BookOpen, Save, X } from 'lucide-react'

export default function AdminBooks() {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    published_date: '',
    copies_available: 1
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchBooks()
  }, [])

  const fetchBooks = async () => {
    try {
      const response = await api.get('/books/')
      const data = response.data.results || response.data
      setBooks(data)
    } catch (error) {
      console.error('Error fetching books:', error)
      setMessage({ type: 'error', text: 'Failed to load books' })
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setFormData({
      title: '',
      author: '',
      isbn: '',
      published_date: '',
      copies_available: 1
    })
    setEditing(null)
    setShowForm(true)
  }

  const handleEdit = (book) => {
    setFormData({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      published_date: book.published_date,
      copies_available: book.copies_available
    })
    setEditing(book.id)
    setShowForm(true)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      if (editing) {
        await api.put(`/books/${editing}/`, formData)
        setMessage({ type: 'success', text: 'Book updated successfully!' })
      } else {
        await api.post('/books/', formData)
        setMessage({ type: 'success', text: 'Book created successfully!' })
      }
      setShowForm(false)
      setEditing(null)
      await fetchBooks()
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 
                      error.response?.data?.error ||
                      Object.values(error.response?.data || {})[0]?.[0] ||
                      'Failed to save book'
      setMessage({ type: 'error', text: errorMsg })
    }
  }

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete "${title}"?`)) {
      return
    }
    try {
      await api.delete(`/books/${id}/`)
      setMessage({ type: 'success', text: 'Book deleted successfully!' })
      await fetchBooks()
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 
                      error.response?.data?.error ||
                      'Failed to delete book'
      setMessage({ type: 'error', text: errorMsg })
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Manage Books</h1>
          <p className="mt-2 text-gray-600">Create, edit, and delete books</p>
        </div>
        <button onClick={handleCreate} className="btn-primary flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Add New Book
        </button>
      </div>

      {message.text && (
        <div className={`card ${message.type === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
          <p className={message.type === 'error' ? 'text-red-800' : 'text-green-800'}>
            {message.text}
          </p>
        </div>
      )}

      {showForm && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {editing ? 'Edit Book' : 'Add New Book'}
          </h2>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Author *
                </label>
                <input
                  type="text"
                  required
                  value={formData.author}
                  onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ISBN *
                </label>
                <input
                  type="text"
                  required
                  value={formData.isbn}
                  onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Published Date *
                </label>
                <input
                  type="date"
                  required
                  value={formData.published_date}
                  onChange={(e) => setFormData({ ...formData, published_date: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Copies Available *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  value={formData.copies_available}
                  onChange={(e) => setFormData({ ...formData, copies_available: parseInt(e.target.value) })}
                  className="input-field"
                />
              </div>
            </div>
            <div className="flex space-x-4">
              <button type="submit" className="btn-primary flex items-center">
                <Save className="h-4 w-4 mr-2" />
                {editing ? 'Update Book' : 'Create Book'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setEditing(null)
                }}
                className="btn-secondary flex items-center"
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Author
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ISBN
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Copies
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {books.map((book) => (
                <tr key={book.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <BookOpen className="h-5 w-5 text-primary-600 mr-2" />
                      <div className="text-sm font-medium text-gray-900">{book.title}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {book.author}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {book.isbn}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      book.copies_available > 0
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {book.copies_available}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(book)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(book.id, book.title)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

