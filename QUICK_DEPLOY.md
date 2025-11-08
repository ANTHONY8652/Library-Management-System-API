# ⚡ QUICK DEPLOY - Get Live in 30 Minutes!

This is the **fastest way** to get your project public. Follow these steps exactly.

## 🎯 Recommended: Render (Backend) + Vercel (Frontend)

Both platforms have **FREE tiers** and are perfect for your project!

---

## 📋 Step 1: Prepare Your Code (5 minutes)

### 1.1 Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 1.2 Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**SAVE THIS KEY!** You'll need it.

---

## 🖥️ Step 2: Deploy Backend to Render (15 minutes)

### 2.1 Create Account
1. Go to https://render.com
2. Sign up with GitHub (easiest)

### 2.2 Create Database
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `library-db`
3. Database: `library_db`
4. Region: Choose closest to you
5. Click **"Create Database"**
6. **SAVE the connection details!**

### 2.3 Deploy Backend
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Settings:
   - **Name**: `library-backend`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```bash
     gunicorn library_management_system.wsgi:application
     ```
   - **Plan**: Free

4. Click **"Advanced"** → **"Add Environment Variable"**
   Add these:
   ```
   DJANGO_SECRET_KEY=<paste-your-generated-key>
   DEBUG=False
   ALLOWED_HOSTS=library-backend.onrender.com
   DB_NAME=library_db
   DB_USER=<from-database>
   DB_PASSWORD=<from-database>
   DB_HOST=<from-database>
   DB_PORT=5432
   ```

5. Click **"Create Web Service"**
6. Wait for deployment (5-10 minutes)
7. **Copy your backend URL** (e.g., `https://library-backend.onrender.com`)

### 2.4 Update CORS Settings
Once backend is live, update `library_management_system/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",  # We'll add this after frontend deploys
    "http://localhost:3000",
]
```
Then push to GitHub again (Render auto-deploys).

---

## 🎨 Step 3: Deploy Frontend to Vercel (10 minutes)

### 3.1 Create Account
1. Go to https://vercel.com
2. Sign up with GitHub

### 3.2 Deploy
1. Click **"Add New"** → **"Project"**
2. Import your GitHub repository
3. Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. Click **"Environment Variables"**
   - Name: `VITE_API_URL`
   - Value: `https://library-backend.onrender.com/api` (your backend URL)
   - Click **"Add"**

5. Click **"Deploy"**
6. Wait 2-3 minutes
7. **Copy your frontend URL** (e.g., `https://library-frontend.vercel.app`)

### 3.3 Update Backend CORS
1. Go back to Render
2. Update environment variable:
   ```
   ALLOWED_HOSTS=library-backend.onrender.com,your-frontend.vercel.app
   ```
3. In your code, update `CORS_ALLOWED_ORIGINS` in settings.py:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://your-frontend.vercel.app",  # Your actual Vercel URL
       "http://localhost:3000",
   ]
   ```
4. Push to GitHub (auto-redeploys)

---

## ✅ Step 4: Test Everything (5 minutes)

1. **Visit your frontend URL**
2. **Register a new user**
3. **Login**
4. **Browse books**
5. **Checkout a book**
6. **Return a book**

If everything works → **YOU'RE LIVE! 🎉**

---

## 🐛 Troubleshooting

### Backend not working?
- Check Render logs: Dashboard → Your Service → Logs
- Verify all environment variables are set
- Check database connection

### Frontend can't connect?
- Verify `VITE_API_URL` is set in Vercel
- Check CORS settings in backend
- Open browser console for errors

### 500 Error?
- Check Render logs
- Verify `DEBUG=False`
- Check `ALLOWED_HOSTS` includes your domain

---

## 🎉 Success!

Your project is now **PUBLIC** and accessible to everyone!

**Frontend URL**: `https://your-frontend.vercel.app`  
**Backend URL**: `https://your-backend.onrender.com`  
**API Docs**: `https://your-backend.onrender.com/`

---

## 📝 Next Steps (Optional)

1. **Custom Domain**: Add your own domain in Vercel/Render settings
2. **SSL**: Automatically handled (HTTPS)
3. **Monitoring**: Check Render/Vercel dashboards
4. **Updates**: Just push to GitHub, auto-deploys!

---

**You've got this! Your project is ready to shine! ✨**

