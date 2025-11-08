# Library Management System - Setup Guide

This guide will help you set up both the backend (Django) and frontend (React) for the Library Management System.

## Prerequisites

- Python 3.12.7
- Node.js 18+ and npm
- PostgreSQL database
- Git

## Backend Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the root directory with:
   ```
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   USE_I18N=True
   USE_TZ=True
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start Django Server**
   ```bash
   python manage.py runserver
   ```
   The backend will be available at `http://localhost:8000`

## Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## Running Both Servers

You'll need to run both servers simultaneously:

**Terminal 1 (Backend):**
```bash
python manage.py runserver
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## First Steps

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Login with your credentials
4. Start browsing and checking out books!

## Troubleshooting

### CORS Errors
If you see CORS errors, make sure:
- `django-cors-headers` is installed: `pip install django-cors-headers`
- CORS settings are configured in `library_management_system/settings.py`
- The frontend is running on `http://localhost:3000`

### Database Connection Errors
- Ensure PostgreSQL is running
- Check your `.env` file has correct database credentials
- Run migrations: `python manage.py migrate`

### Frontend Build Errors
- Make sure Node.js 18+ is installed
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check that all dependencies in `package.json` are compatible

## API Endpoints

The frontend communicates with these backend endpoints:
- `POST /register/` - User registration
- `POST /login/` - User login
- `POST /logout/` - User logout
- `GET /books/` - List all books
- `GET /books/:id/` - Get book details
- `GET /available-books/` - List available books
- `POST /checkout/` - Checkout a book
- `PATCH /return/:id/` - Return a book
- `GET /overdue-books/` - Get overdue books

## Features

- ✅ User authentication (Register/Login/Logout)
- ✅ Browse and search books
- ✅ Book checkout and return
- ✅ View borrowed books
- ✅ Track overdue books
- ✅ Responsive design
- ✅ Beautiful, modern UI

