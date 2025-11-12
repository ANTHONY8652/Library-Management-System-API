# 📚 Library Management System

A modern, full-stack library management system built with Django REST Framework and React. This system provides a comprehensive solution for managing books, users, and transactions in a library environment.

![License](https://img.shields.io/badge/license-BSD-blue)
![Python](https://img.shields.io/badge/python-3.12.7-blue)
![Django](https://img.shields.io/badge/django-5.0.7-green)
![React](https://img.shields.io/badge/react-18.2.0-blue)
![PostgreSQL](https://img.shields.io/badge/postgresql-16+-blue)
![Vite](https://img.shields.io/badge/vite-6.4.1-purple)
![Tailwind CSS](https://img.shields.io/badge/tailwind-3.3.6-teal)

## ✨ Features

### 🔐 Authentication & Authorization
- **User Registration & Login** - Secure JWT-based authentication
- **Role-Based Access Control** - Admin and Member roles with different permissions
- **Token Management** - Automatic token refresh and secure logout
- **Profile Management** - View and manage user profiles

### 📖 Book Management
- **Browse Books** - View all available books with pagination
- **Search & Filter** - Search by title, author, or ISBN
- **Book Details** - Detailed view of each book with availability status
- **Admin Book Management** - Create, edit, and delete books (Admin only)

### 📚 Transaction Management
- **Book Checkout** - Borrow books with automatic due date calculation
- **Book Return** - Return books with penalty calculation for overdue items
- **My Books** - View currently borrowed books
- **Transaction History** - Complete history of all transactions
- **Overdue Tracking** - Automatic tracking and penalty calculation

### 📊 Dashboard & Analytics
- **Library Statistics** - Overview of books, users, and transactions
- **Quick Actions** - Easy access to common tasks
- **Responsive Design** - Beautiful, modern UI that works on all devices

### 🔒 Security Features
- **Environment-Based Configuration** - All secrets in environment variables
- **CORS Protection** - Configured for secure cross-origin requests
- **Security Headers** - Auto-enabled in production mode
- **JWT Token Rotation** - Enhanced security with token rotation
- **Input Validation** - Comprehensive validation on all endpoints

## 🛠️ Tech Stack

### Backend

![Python](https://img.shields.io/badge/Python-3.12.7-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0.7-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.14.0-red?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | Django | 5.0.7 | High-level Python web framework |
| **API** | Django REST Framework | 3.14.0 | Powerful toolkit for building Web APIs |
| **Database** | PostgreSQL | 16+ | Robust relational database |
| **Authentication** | JWT (djangorestframework-simplejwt) | 5.2.2 | Secure token-based authentication |
| **API Docs** | drf-yasg | 1.21.7 | Swagger/OpenAPI documentation |
| **Filtering** | django-filter | 23.2 | Advanced filtering and search capabilities |
| **CORS** | django-cors-headers | 4.3.1 | Handling Cross-Origin Resource Sharing |
| **Environment** | python-dotenv | 1.0.0 | Environment variable management |
| **Server** | Gunicorn | 21.2.0 | Production WSGI HTTP Server |
| **Static Files** | WhiteNoise | 6.6.0 | Static file serving for production |

### Frontend

![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-6.4.1-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.3.6-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-6.20.0-CA4245?style=for-the-badge&logo=react-router&logoColor=white)

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | React | 18.2.0 | Modern UI library with hooks |
| **Build Tool** | Vite | 6.4.1 | Fast build tool and dev server |
| **Routing** | React Router | 6.20.0 | Client-side routing |
| **Styling** | Tailwind CSS | 3.3.6 | Utility-first CSS framework |
| **HTTP Client** | Axios | 1.6.2 | Promise-based HTTP client |
| **Icons** | Lucide React | 0.294.0 | Beautiful icon library |
| **CSS Processing** | PostCSS | 8.4.32 | CSS transformer |
| **Autoprefixer** | Autoprefixer | 10.4.16 | CSS vendor prefixing |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **npm** | Package management |
| **pip** | Python package management |
| **PostgreSQL** | Database management |
| **VS Code / Cursor** | Code editor |

### Deployment

| Platform | Purpose |
|----------|---------|
| **Render** | Backend deployment (Django) |
| **Vercel** | Frontend deployment (React) |
| **PostgreSQL** | Database hosting |

### Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   React Frontend│ ◄─────► │  Django REST API │ ◄─────► │   PostgreSQL    │
│   (Vite + React)│  HTTP   │  (DRF + JWT)     │  SQL    │    Database     │
└─────────────────┘         └──────────────────┘         └─────────────────┘
         │                           │
         │                           │
    ┌────▼────┐                ┌────▼────┐
    │ Vercel  │                │ Render  │
    │ (CDN)   │                │ (Server)│
    └─────────┘                └─────────┘
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12.7** or higher
- **Node.js 18+** and npm
- **PostgreSQL** database
- **Git** for version control

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Library-Management-System-API
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Required
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Email Configuration (for password reset)
# Option 1: Brevo API (Recommended - works on Render)
BREVO_API_KEY=your-brevo-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
DEFAULT_FROM_NAME=Library Management System

# Option 2: SMTP (Alternative)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_USE_SSL=False
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
```

**Important:** Generate a strong secret key for production:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Run Database Migrations

```bash
python manage.py migrate
```

#### Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

#### Start Django Server

```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Navigate to Frontend Directory

```bash
cd frontend
```

#### Install Dependencies

```bash
npm install
```

#### Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Running Both Servers

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

## 📖 Usage Guide

### First Steps

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Login with your credentials
4. Start browsing and checking out books!

### For Regular Users (Members)

- **Browse Books**: View all available books in the library
- **Search Books**: Use the search bar to find books by title, author, or ISBN
- **Checkout Books**: Click on a book to view details and checkout
- **My Books**: View your borrowed books and return them when done
- **Transaction History**: View your complete borrowing history
- **Profile**: View your profile information

### For Administrators

- **All Member Features** - Plus:
- **Manage Books**: Create, edit, and delete books
- **Extended Loan Period**: 30 days instead of 14 days
- **Full Access**: Access to all library management features

## 🔌 API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `POST /api/token/refresh/` - Refresh JWT token

### Books
- `GET /api/books/` - List all books (paginated)
- `POST /api/books/` - Create a book (Admin only)
- `GET /api/books/:id/` - Get book details  
- `PUT /api/books/:id/` - Update a book (Admin only)
- `DELETE /api/books/:id/` - Delete a book (Admin only)
- `GET /api/available-books/` - List available books (paginated)

### Transactions
- `POST /api/checkout/` - Checkout a book
- `PATCH /api/return/:id/` - Return a book
- `GET /api/my-books/` - Get currently borrowed books (paginated)
- `GET /api/transaction-history/` - Get transaction history (paginated)
- `GET /api/overdue-books/` - Get overdue books (paginated)

### User Profile
- `GET /api/my-profile/` - Get current user's profile
- `GET /api/user-profiles/` - List all user profiles (Admin only)
- `GET /api/user-profiles/:id/` - Get user profile details

### API Documentation

- **Swagger UI**: `http://localhost:8000/`
- **ReDoc**: `http://localhost:8000/redoc/`

## 📁 Project Structure

```
Library-Management-System-API/
├── library_api/              # Django app
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # URL routing
│   ├── permissions.py       # Custom permissions
│   └── migrations/          # Database migrations
├── library_management_system/  # Django project settings
│   ├── settings.py          # Project settings
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py              # WSGI configuration
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── contexts/        # React contexts
│   │   ├── pages/           # Page components
│   │   └── services/        # API services
│   ├── package.json
│   └── vite.config.js
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔒 Security

### Security Features

- ✅ **Environment Variables** - All secrets stored in `.env` file
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **CORS Protection** - Configured for secure cross-origin requests
- ✅ **Security Headers** - Auto-enabled in production
- ✅ **Token Rotation** - Enhanced security with refresh token rotation
- ✅ **Input Validation** - Comprehensive validation on all inputs
- ✅ **Role-Based Access** - Proper permission checks on all endpoints

### Production Deployment

Before deploying to production:

1. **Set Environment Variables:**
   ```env
   DJANGO_SECRET_KEY=<strong-random-key>
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DB_PASSWORD=<strong-password>
   ```

2. **Security Settings** - Automatically enabled when `DEBUG=False`:
   - CSRF protection
   - Secure cookies
   - SSL redirect
   - HSTS headers
   - XSS protection

3. **Database** - Use a production-grade database (PostgreSQL recommended)

4. **Frontend** - Update API URLs to use environment variables

### Required Environment Variables for Production

```env
DJANGO_SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FRONTEND_URL=https://yourdomain.com
BREVO_API_KEY=your-brevo-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
DB_PASSWORD=<strong-password>
```

## 🐛 Troubleshooting

### CORS Errors

If you see CORS errors:
- Ensure `django-cors-headers` is installed: `pip install django-cors-headers`
- Check CORS settings in `library_management_system/settings.py`
- Verify frontend is running on `http://localhost:3000`

### Database Connection Errors

- Ensure PostgreSQL is running
- Check your `.env` file has correct database credentials
- Run migrations: `python manage.py migrate`

### Frontend Build Errors

- Make sure Node.js 18+ is installed
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check that all dependencies in `package.json` are compatible

### Authentication Issues

- Clear browser localStorage
- Check that backend is running on `http://localhost:8000`
- Verify JWT token is being sent in request headers

## 📝 Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Building Frontend for Production

```bash
cd frontend
npm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the BSD License.

## 👥 Authors

- **Your Name** - *Initial work*

## 🙏 Acknowledgments

- Django REST Framework team
- React team
- Tailwind CSS team
- All contributors and open-source libraries used

## 📞 Support

For support, email your-email@example.com or open an issue in the repository.

---

**Note:** This is a development version. For production deployment, ensure all security settings are properly configured and environment variables are set correctly.
