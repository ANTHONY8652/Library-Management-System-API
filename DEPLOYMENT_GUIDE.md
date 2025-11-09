# 🚀 Deployment Guide - Make It Public!

This guide will help you deploy your Library Management System to production. I'll provide multiple options, from easiest to most flexible.

## ⚡ Quick Deploy (30 Minutes)

**Fastest way to get live:**

1. **Backend to Render** (15 min)
   - Create account at https://render.com
   - New PostgreSQL database
   - New Web Service (Django)
   - Add environment variables
   - Deploy!

2. **Frontend to Vercel** (10 min)
   - Create account at https://vercel.com
   - Import GitHub repo
   - Set `VITE_API_URL` environment variable
   - Deploy!

3. **Test** (5 min)
   - Visit your URLs
   - Test registration/login
   - Verify everything works

**See `QUICK_DEPLOY.md` for detailed step-by-step instructions.**

---

## 🎯 Recommended Deployment Strategy

**Best Option for Beginners:**
- **Frontend**: Vercel (Free, excellent for React)
- **Backend**: Render (Free tier available)
- **Database**: Render PostgreSQL (Free tier)

**Alternative Options:**
- Railway (hosts everything together)
- Heroku (paid, but very reliable)
- DigitalOcean (more control)
- Supabase + Hostinger Domain (see `SUPABASE_HOSTINGER_GUIDE.md`)

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All environment variables are set
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Frontend API URLs updated
- [ ] CORS settings updated
- [ ] Security headers enabled

---

## 🌐 Option 1: Vercel (Frontend) + Render (Backend) - RECOMMENDED

### Step 1: Deploy Backend to Render

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub (recommended)

2. **Create PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name: `library-db`
   - Database: `library_db`
   - User: `library_user`
   - Region: Choose closest to you
   - **Save the connection string!**

3. **Create Web Service (Backend)**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name**: `library-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn library_management_system.wsgi:application`
     - **Plan**: Free (or paid for better performance)

4. **Add Environment Variables in Render**
   ```
   DJANGO_SECRET_KEY=<generate-strong-key>
   DEBUG=False
   ALLOWED_HOSTS=library-backend.onrender.com,yourdomain.com
   DB_NAME=library_db
   DB_USER=library_user
   DB_PASSWORD=<from-render-database>
   DB_HOST=<from-render-database>
   DB_PORT=5432
   ```

5. **Add Build Command**
   - In Render settings, add:
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```

6. **Install Gunicorn**
   - Add to `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```

### Step 2: Deploy Frontend to Vercel

1. **Create Vercel Account**
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Update Frontend API URL**
   - Create `frontend/.env.production`:
   ```
   VITE_API_URL=https://library-backend.onrender.com/api
   ```

3. **Update `frontend/src/services/api.js`**
   ```javascript
   const api = axios.create({
     baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
     headers: {
       'Content-Type': 'application/json',
     },
   })
   ```

4. **Deploy to Vercel**
   - Import your GitHub repository
   - Root Directory: `frontend`
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

5. **Add Environment Variable in Vercel**
   - Go to Project Settings → Environment Variables
   - Add: `VITE_API_URL=https://library-backend.onrender.com/api`

---

## 🚂 Option 2: Railway (All-in-One) - EASIEST

Railway can host everything together.

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add PostgreSQL Database**
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway automatically provides connection string

4. **Configure Backend Service**
   - Railway auto-detects Django
   - Add environment variables:
     ```
     DJANGO_SECRET_KEY=<generate-key>
     DEBUG=False
     ALLOWED_HOSTS=*.railway.app,yourdomain.com
     ```
   - Railway will auto-populate DB_* variables from PostgreSQL

5. **Add Build Command**
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```

6. **Add Start Command**
   ```
   gunicorn library_management_system.wsgi:application --bind 0.0.0.0:$PORT
   ```

7. **Deploy Frontend**
   - Add another service
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve -s dist -l $PORT`
   - Add environment variable: `VITE_API_URL=<your-backend-url>/api`

---

## 🐳 Option 3: Docker + Any Platform

### Create Dockerfile for Backend

Create `Dockerfile` in root:
```dockerfile
FROM python:3.12.7-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "library_management_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Create Dockerfile for Frontend

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🔧 Required Code Changes

### 1. Update `requirements.txt`
Add production server:
```
gunicorn==21.2.0
whitenoise==6.6.0  # For static files
```

### 2. Update `settings.py`
Add at the end:
```python
# Static files (WhiteNoise)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add WhiteNoise middleware (after SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]
```

### 3. Update Frontend API Configuration

Create `frontend/.env.production`:
```
VITE_API_URL=https://your-backend-url.com/api
```

Update `frontend/src/services/api.js`:
```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### 4. Update Token Refresh URL

In `frontend/src/services/api.js`, update:
```javascript
const response = await axios.post(
  `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/api/token/refresh/`,
  { refresh: refresh }
)
```

---

## 🔐 Security Configuration

### Generate Secret Key
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Production Settings Checklist
- ✅ `DEBUG=False`
- ✅ `ALLOWED_HOSTS` includes your domain
- ✅ `SECRET_KEY` from environment
- ✅ Database credentials from environment
- ✅ CORS_ALLOWED_ORIGINS includes frontend URL
- ✅ Security headers enabled (auto when DEBUG=False)

---

## 📝 Step-by-Step: Render + Vercel (Detailed)

### Backend on Render

1. **Push code to GitHub** (if not already)

2. **Create Render account** → https://render.com

3. **Create PostgreSQL Database:**
   - New + → PostgreSQL
   - Name: `library-db`
   - Save the **Internal Database URL**

4. **Create Web Service:**
   - New + → Web Service
   - Connect GitHub repo
   - Name: `library-backend`
   - Environment: `Python 3`
   - Build Command:
     ```bash
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - Start Command:
     ```bash
     gunicorn library_management_system.wsgi:application
     ```

5. **Environment Variables:**
   ```
   DJANGO_SECRET_KEY=<your-generated-key>
   DEBUG=False
   ALLOWED_HOSTS=library-backend.onrender.com
   DATABASE_URL=<from-postgres-service>
   ```
   
   Render auto-parses `DATABASE_URL`, but you can also set:
   ```
   DB_NAME=library_db
   DB_USER=library_user
   DB_PASSWORD=<password>
   DB_HOST=<host>
   DB_PORT=5432
   ```

6. **Update CORS in settings.py:**
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://your-frontend.vercel.app",
       "http://localhost:3000",  # Keep for local dev
   ]
   ```

### Frontend on Vercel

1. **Update API service:**
   - Edit `frontend/src/services/api.js`
   - Use environment variable for base URL

2. **Create Vercel account** → https://vercel.com

3. **Import GitHub repo:**
   - New Project → Import Git Repository
   - Root Directory: `frontend`
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Environment Variables:**
   - `VITE_API_URL=https://library-backend.onrender.com/api`

5. **Deploy!**

---

## 🧪 Testing Your Deployment

1. **Test Backend:**
   - Visit: `https://your-backend.onrender.com/`
   - Should see Swagger UI
   - Test API endpoints

2. **Test Frontend:**
   - Visit: `https://your-frontend.vercel.app`
   - Try registering a user
   - Try logging in
   - Test book checkout

3. **Check Logs:**
   - Render: Dashboard → Your Service → Logs
   - Vercel: Project → Deployments → View Function Logs

---

## 🐛 Common Issues & Fixes

### Issue: CORS Errors
**Fix:** Update `CORS_ALLOWED_ORIGINS` in settings.py with your frontend URL

### Issue: Static Files Not Loading
**Fix:** 
- Add `whitenoise` to requirements.txt
- Run `collectstatic` in build command
- Add WhiteNoise middleware

### Issue: Database Connection Failed
**Fix:** 
- Check database credentials
- Ensure database is running
- Verify connection string format

### Issue: 500 Internal Server Error
**Fix:**
- Check Render logs
- Verify all environment variables are set
- Ensure `DEBUG=False` in production
- Check `ALLOWED_HOSTS` includes your domain

### Issue: Frontend Can't Connect to Backend
**Fix:**
- Verify `VITE_API_URL` is set correctly
- Check CORS settings
- Ensure backend URL is accessible

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Starting |
|----------|-----------|---------------|
| **Render** | ✅ Yes (limited) | $7/month |
| **Vercel** | ✅ Yes | $20/month |
| **Railway** | ✅ $5 credit/month | $5/month |
| **Heroku** | ❌ No | $7/month |
| **DigitalOcean** | ❌ No | $6/month |

**Recommended for Free:**
- Render (Backend) + Vercel (Frontend) = **FREE**

---

## 🎯 Quick Start Commands

### Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Test Locally with Production Settings
```bash
export DEBUG=False
export ALLOWED_HOSTS=localhost,127.0.0.1
python manage.py runserver
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 📞 Need Help?

If you encounter issues:
1. Check platform logs
2. Verify environment variables
3. Test API endpoints directly
4. Check CORS configuration
5. Verify database connection

---

## 🎉 Success Checklist

After deployment, verify:
- [ ] Backend accessible at your URL
- [ ] Frontend accessible at your URL
- [ ] User registration works
- [ ] User login works
- [ ] Books can be viewed
- [ ] Books can be checked out
- [ ] Books can be returned
- [ ] Admin features work (if admin user)
- [ ] No console errors in browser
- [ ] API calls succeed

---

**You've got this! Your project is ready to go live! 🚀**

