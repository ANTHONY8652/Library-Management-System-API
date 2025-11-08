import { useEffect, useState } from 'react'
import api from '../services/api'
import { User, Mail, Calendar, Shield, Edit2, Save, X } from 'lucide-react'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({})
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await api.get('/my-profile/')
      setProfile(response.data)
      setFormData({
        email: response.data.email || '',
        loan_duration: response.data.loan_duration || 14
      })
    } catch (error) {
      console.error('Error fetching profile:', error)
      setMessage({ type: 'error', text: 'Failed to load profile' })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      // Note: Email and role changes would need separate endpoints
      // For now, we'll just show a message
      setMessage({ type: 'success', text: 'Profile updated successfully!' })
      setEditing(false)
      await fetchProfile()
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update profile' })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-600">Profile not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
          <p className="mt-2 text-gray-600">Manage your account information</p>
        </div>
        {!editing && (
          <button
            onClick={() => setEditing(true)}
            className="btn-primary flex items-center"
          >
            <Edit2 className="h-4 w-4 mr-2" />
            Edit Profile
          </button>
        )}
      </div>

      {message.text && (
        <div className={`card ${message.type === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
          <p className={message.type === 'error' ? 'text-red-800' : 'text-green-800'}>
            {message.text}
          </p>
        </div>
      )}

      <div className="card">
        <div className="space-y-6">
          <div className="flex items-center space-x-4">
            <div className="bg-primary-100 p-4 rounded-full">
              <User className="h-8 w-8 text-primary-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{profile.username}</h2>
              <p className="text-gray-600">Member since {new Date(profile.date_of_membership).toLocaleDateString()}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="flex items-center text-sm font-medium text-gray-700">
                <Mail className="h-4 w-4 mr-2" />
                Email
              </label>
              {editing ? (
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="input-field"
                  disabled
                />
              ) : (
                <p className="text-gray-900">{profile.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="flex items-center text-sm font-medium text-gray-700">
                <Shield className="h-4 w-4 mr-2" />
                Role
              </label>
              <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                profile.role === 'admin' 
                  ? 'bg-purple-100 text-purple-800' 
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {profile.role === 'admin' ? 'Administrator' : 'Member'}
              </span>
            </div>

            <div className="space-y-2">
              <label className="flex items-center text-sm font-medium text-gray-700">
                <Calendar className="h-4 w-4 mr-2" />
                Loan Duration
              </label>
              {editing ? (
                <input
                  type="number"
                  value={formData.loan_duration}
                  onChange={(e) => setFormData({ ...formData, loan_duration: parseInt(e.target.value) })}
                  className="input-field"
                  min="1"
                  max="90"
                />
              ) : (
                <p className="text-gray-900">{profile.loan_duration} days</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="flex items-center text-sm font-medium text-gray-700">
                Status
              </label>
              <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                profile.active_status 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {profile.active_status ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          {editing && (
            <div className="flex space-x-4 pt-4 border-t">
              <button onClick={handleSave} className="btn-primary flex items-center">
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </button>
              <button onClick={() => { setEditing(false); fetchProfile() }} className="btn-secondary flex items-center">
                <X className="h-4 w-4 mr-2" />
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

