import { Link } from 'react-router-dom'
import { BookOpen, Search, Library, Sparkles, ArrowRight, Heart } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Home() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-rose-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <BookOpen className="h-20 w-20 text-amber-600 animate-bounce" />
              <Sparkles className="h-8 w-8 text-yellow-400 absolute -top-2 -right-2 animate-pulse" />
            </div>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            Welcome to the <span className="text-amber-600">Magical World</span> of Books!
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-700 mb-8 max-w-3xl mx-auto">
            Where every page is an adventure, every chapter a journey, and every book a treasure waiting to be discovered! 📚✨
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Link
              to="/books"
              className="inline-flex items-center px-8 py-4 bg-amber-600 text-white text-lg font-semibold rounded-lg hover:bg-amber-700 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl"
            >
              <Library className="h-6 w-6 mr-2" />
              Explore Our Collection
              <ArrowRight className="h-6 w-6 ml-2" />
            </Link>
            
            {!user && (
              <Link
                to="/register"
                className="inline-flex items-center px-8 py-4 bg-white text-amber-600 text-lg font-semibold rounded-lg border-2 border-amber-600 hover:bg-amber-50 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                <Heart className="h-6 w-6 mr-2" />
                Join Our Library
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Browse Freely</h3>
            <p className="text-gray-600">
              Discover thousands of books from classic literature to modern bestsellers. No account needed to explore!
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Search & Find</h3>
            <p className="text-gray-600">
              Find exactly what you're looking for with our powerful search. Search by title, author, or ISBN!
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow text-center">
            <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Library className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Borrow & Enjoy</h3>
            <p className="text-gray-600">
              Sign up to checkout books and take them home. It's free, it's easy, and it's magical!
            </p>
          </div>
        </div>
      </div>

      {/* Quote Section */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="bg-gradient-to-r from-amber-100 to-orange-100 rounded-2xl p-12 shadow-lg">
          <p className="text-3xl md:text-4xl font-serif text-gray-800 mb-4 italic">
            "A book is a dream that you hold in your hand."
          </p>
          <p className="text-xl text-gray-600">— Neil Gaiman</p>
        </div>
      </div>

      {/* Call to Action */}
      {!user && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <div className="bg-white rounded-2xl p-12 shadow-xl">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Ready to Start Your Reading Journey?
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Create a free account and unlock the full library experience!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="inline-flex items-center px-8 py-4 bg-amber-600 text-white text-lg font-semibold rounded-lg hover:bg-amber-700 transition-all transform hover:scale-105 shadow-lg"
              >
                Sign Up Now
                <ArrowRight className="h-6 w-6 ml-2" />
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center px-8 py-4 bg-gray-100 text-gray-700 text-lg font-semibold rounded-lg hover:bg-gray-200 transition-all transform hover:scale-105"
              >
                Already have an account? Login
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

