# 🚀 Deployment Checklist - Get Live in 30 Minutes!

## ✅ Pre-Deployment Setup

### Step 1: Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**SAVE THIS KEY!** You'll need it for Render.

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

---

## 🆓 FREE Deployment (Recommended - $0/month)

### Option A: Render + Vercel (Easiest)

#### Backend on Render (15 min)

1. **Create Account**: https://render.com (Sign up with GitHub)

2. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `library-db`
   - Plan: **Free**
   - Region: Choose closest to you
   - Click "Create Database"
   - **SAVE** the connection details (you'll see them after creation)

3. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
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
     - **Plan**: **Free**

4. **Add Environment Variables** (in Render dashboard):
   ```
   DJANGO_SECRET_KEY=<paste-your-generated-key-here>
   DEBUG=False
   ALLOWED_HOSTS=library-backend.onrender.com
   DB_NAME=<from-database-details>
   DB_USER=<from-database-details>
   DB_PASSWORD=<from-database-details>
   DB_HOST=<from-database-details>
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
   
   **Note**: Replace `your-frontend.vercel.app` with your actual Vercel URL after deploying frontend.

5. **Deploy**: Click "Create Web Service" and wait 5-10 minutes

6. **Copy your backend URL**: `https://library-backend.onrender.com`

#### Frontend on Vercel (10 min)

1. **Create Account**: https://vercel.com (Sign up with GitHub)

2. **Import Project**:
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Settings:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
     - **Install Command**: `npm install`

3. **Add Environment Variable**:
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     VITE_API_URL=https://library-backend.onrender.com/api
     ```
   - Replace `library-backend.onrender.com` with your actual Render backend URL

4. **Deploy**: Click "Deploy" and wait 2-3 minutes

5. **Update CORS in Render**:
   - Go back to Render dashboard
   - Update `CORS_ALLOWED_ORIGINS` environment variable:
     ```
     CORS_ALLOWED_ORIGINS=https://your-project.vercel.app
     ```
   - Redeploy backend

---

## 💰 Paid Option: Custom Domain with Hostinger (Optional)

**Cost**: ~$10-15/year for a domain

### When to Use:
- You want a custom domain (e.g., `yourlibrary.com`)
- You want a professional look
- You're ready to invest in branding

### Setup:
1. **Buy Domain**: https://hostinger.com
2. **Point Domain to Render**:
   - In Render: Settings → Custom Domains → Add your domain
   - Update DNS in Hostinger to point to Render
3. **Update ALLOWED_HOSTS**:
   ```
   ALLOWED_HOSTS=library-backend.onrender.com,yourdomain.com,www.yourdomain.com
   ```
4. **Point Frontend Domain to Vercel**:
   - In Vercel: Settings → Domains → Add your domain
   - Update DNS in Hostinger

**See `SUPABASE_HOSTINGER_GUIDE.md` for detailed instructions.**

---

## ✅ Post-Deployment Checklist

- [ ] Backend is accessible at `https://library-backend.onrender.com`
- [ ] Frontend is accessible at `https://your-project.vercel.app`
- [ ] Can register a new user
- [ ] Can login
- [ ] Can view books
- [ ] Can checkout a book
- [ ] CORS is working (no errors in browser console)
- [ ] API endpoints are accessible

---

## 🐛 Troubleshooting

### Backend Issues:
- **"Invalid HTTP_HOST header"**: Update `ALLOWED_HOSTS` in Render
- **Database connection error**: Check DB_* environment variables
- **Static files not loading**: Run `python manage.py collectstatic --noinput` in build command

### Frontend Issues:
- **API calls failing**: Check `VITE_API_URL` in Vercel environment variables
- **CORS errors**: Update `CORS_ALLOWED_ORIGINS` in Render with your Vercel URL

### General:
- Check logs in Render dashboard → Your Service → Logs
- Check logs in Vercel dashboard → Your Project → Deployments → View Logs

---

## 📝 Environment Variables Summary

### Render (Backend):
```
DJANGO_SECRET_KEY=<your-generated-key>
DEBUG=False
ALLOWED_HOSTS=library-backend.onrender.com
DB_NAME=<from-render-database>
DB_USER=<from-render-database>
DB_PASSWORD=<from-render-database>
DB_HOST=<from-render-database>
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Vercel (Frontend):
```
VITE_API_URL=https://library-backend.onrender.com/api
```

---

## 🎉 You're Live!

Once deployed, share your URLs:
- **Frontend**: `https://your-project.vercel.app`
- **Backend API**: `https://library-backend.onrender.com/api`
- **API Docs**: `https://library-backend.onrender.com/api/swagger/`

---

**Need Help?** Check the detailed guides:
- `QUICK_DEPLOY.md` - Step-by-step instructions
- `DEPLOYMENT_GUIDE.md` - Comprehensive guide
- `ALLOWED_HOSTS_DEPLOYMENT_CHEATSHEET.md` - Troubleshooting ALLOWED_HOSTS

