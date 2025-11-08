# Library Management System - Frontend

A beautiful, modern, and elegant React frontend for the Library Management System API.

## Features

- 🎨 **Beautiful UI** - Clean, modern design with Tailwind CSS
- 🔐 **Authentication** - Secure login and registration with JWT
- 📚 **Book Management** - Browse, search, and checkout books
- 📖 **My Books** - Track your borrowed books and returns
- 📊 **Dashboard** - Overview of library statistics
- 📱 **Responsive** - Works perfectly on all devices

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon library

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

3. **Build for Production**
   ```bash
   npm run build
   ```

## Configuration

Make sure your Django backend is running on `http://localhost:8000`. If your backend runs on a different port, update the `baseURL` in `src/services/api.js`.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   └── Layout.jsx   # Main layout with navigation
│   ├── contexts/        # React contexts
│   │   └── AuthContext.jsx  # Authentication context
│   ├── pages/          # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Books.jsx
│   │   ├── BookDetail.jsx
│   │   └── MyBooks.jsx
│   ├── services/       # API services
│   │   └── api.js      # Axios configuration
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Browse Books**: View all available books in the library
3. **Search**: Use the search bar to find books by title, author, or ISBN
4. **Checkout**: Click on a book to view details and checkout
5. **My Books**: View your borrowed books and return them when done
6. **Dashboard**: See library statistics and quick actions

## API Endpoints Used

- `POST /register/` - User registration
- `POST /login/` - User login
- `POST /logout/` - User logout
- `GET /books/` - List all books
- `GET /books/:id/` - Get book details
- `GET /available-books/` - List available books
- `POST /checkout/` - Checkout a book
- `PATCH /return/:id/` - Return a book
- `GET /overdue-books/` - Get overdue books

## Notes

- The frontend uses JWT tokens stored in localStorage for authentication
- Tokens are automatically refreshed when they expire
- All API calls include authentication headers automatically

