# 🚀 Supabase + Hostinger Domain Deployment Guide

This guide shows you how to use **Supabase** for your database and connect a **Hostinger domain** to your deployed application.

## 🎯 Architecture Overview

```
┌─────────────────┐
│   Hostinger     │  → Custom Domain (yourdomain.com)
│     Domain      │
└────────┬────────┘
         │
         ├──→ Frontend (Vercel/Netlify) → yourdomain.com
         │
         └──→ Backend (Render/Railway) → api.yourdomain.com
                  │
                  └──→ Supabase PostgreSQL Database
```

## 📋 What You'll Need

- ✅ Supabase account (FREE tier available)
- ✅ Hostinger domain (paid)
- ✅ Render/Railway account (for Django backend - FREE)
- ✅ Vercel/Netlify account (for React frontend - FREE)

---

## 🗄️ Step 1: Set Up Supabase Database (10 minutes)

### 1.1 Create Supabase Account
1. Go to https://supabase.com
2. Sign up with GitHub (easiest)
3. Create a new project

### 1.2 Create Project
1. Click **"New Project"**
2. Settings:
   - **Name**: `library-management`
   - **Database Password**: Create a strong password (SAVE IT!)
   - **Region**: Choose closest to you
   - **Plan**: Free (or Pro if you need more)
3. Click **"Create new project"**
4. Wait 2-3 minutes for setup

### 1.3 Get Database Connection String
1. Go to **Settings** → **Database**
2. Scroll to **"Connection string"**
3. Copy the **"URI"** connection string
   - Format: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`
4. **SAVE THIS!** You'll need it for Django

### 1.4 Update Django Settings for Supabase

Update `library_management_system/settings.py`:

```python
import os
from urllib.parse import urlparse

# Supabase Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')  # From Supabase

if DATABASE_URL:
    # Parse the Supabase connection string
    db_info = urlparse(DATABASE_URL)
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_info.path[1:],  # Remove leading '/'
            'USER': db_info.username,
            'PASSWORD': db_info.password,
            'HOST': db_info.hostname,
            'PORT': db_info.port or 5432,
            'OPTIONS': {
                'sslmode': 'require',  # Supabase requires SSL
            },
        }
    }
else:
    # Fallback to environment variables (for local dev)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv("DB_NAME"),
            'USER': os.getenv("DB_USER"),
            'PASSWORD': os.getenv("DB_PASSWORD"),
            'HOST': os.getenv("DB_HOST"),
            'PORT': os.getenv("DB_PORT"),
        }
    }
```

### 1.5 Run Migrations
```bash
python manage.py migrate
```

---

## 🌐 Step 2: Deploy Backend to Render (15 minutes)

### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### 2.2 Deploy Django Backend
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Settings:
   - **Name**: `library-backend`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```bash
     gunicorn library_management_system.wsgi:application
     ```

### 2.3 Add Environment Variables
In Render dashboard, add:
```
DJANGO_SECRET_KEY=<your-generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=library-backend.onrender.com,api.yourdomain.com,yourdomain.com
DATABASE_URL=<supabase-connection-string>
```

**Note**: Replace `yourdomain.com` with your actual Hostinger domain.

### 2.4 Deploy
Click **"Create Web Service"** and wait for deployment.

---

## 🎨 Step 3: Deploy Frontend to Vercel (10 minutes)

### 3.1 Deploy to Vercel
1. Go to https://vercel.com
2. Import your GitHub repository
3. Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.2 Add Environment Variable
```
VITE_API_URL=https://api.yourdomain.com/api
```
(We'll update this after domain setup)

### 3.3 Deploy
Click **"Deploy"** and wait.

---

## 🌍 Step 4: Configure Hostinger Domain (20 minutes)

### 4.1 Buy Domain on Hostinger
1. Go to https://hostinger.com
2. Search for your desired domain
3. Purchase domain
4. Complete checkout

### 4.2 Access Hostinger Control Panel
1. Log in to Hostinger
2. Go to **"Domains"** → Your domain
3. Click **"Manage"** → **"DNS / Name Servers"**

### 4.3 Configure DNS Records

#### For Frontend (Vercel):
1. In Vercel dashboard, go to your project
2. Go to **Settings** → **Domains**
3. Add your domain: `yourdomain.com`
4. Vercel will show you DNS records to add:
   - Type: `A` or `CNAME`
   - Name: `@` or `www`
   - Value: (Vercel provides this)

5. In Hostinger DNS settings, add:
   ```
   Type: A
   Name: @
   Value: <Vercel's IP address>
   TTL: 3600
   
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   TTL: 3600
   ```

#### For Backend API (Subdomain):
1. In Render dashboard, go to your service
2. Go to **Settings** → **Custom Domain**
3. Add: `api.yourdomain.com`

4. In Hostinger DNS settings, add:
   ```
   Type: CNAME
   Name: api
   Value: <render-provided-value>.onrender.com
   TTL: 3600
   ```

### 4.4 Update SSL Certificates
- **Vercel**: Automatically provisions SSL (wait 5-10 minutes)
- **Render**: Automatically provisions SSL (wait 5-10 minutes)

### 4.5 Update Environment Variables

**In Vercel:**
```
VITE_API_URL=https://api.yourdomain.com/api
```

**In Render:**
```
ALLOWED_HOSTS=library-backend.onrender.com,api.yourdomain.com,yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 🔧 Step 5: Update Code for Custom Domain

### 5.1 Update CORS Settings

In `library_management_system/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "http://localhost:3000",  # Keep for local dev
]

CORS_ALLOW_CREDENTIALS = True
```

### 5.2 Update Frontend API URL

The frontend already uses environment variables, so just update in Vercel dashboard.

---

## ✅ Step 6: Test Everything (5 minutes)

1. **Visit**: `https://yourdomain.com`
2. **Test Registration**
3. **Test Login**
4. **Test Book Operations**
5. **Check API**: `https://api.yourdomain.com/`

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| **Supabase** | FREE | 500MB database, 2GB bandwidth |
| **Render** | FREE | 750 hours/month (enough for 24/7) |
| **Vercel** | FREE | Unlimited deployments |
| **Hostinger Domain** | ~$10-15/year | Depends on TLD |
| **Total** | **~$10-15/year** | Just domain cost! |

**Optional Upgrades:**
- Supabase Pro: $25/month (if you need more)
- Render Paid: $7/month (if free tier not enough)
- Hostinger Hosting: $2-5/month (if you want hosting too)

---

## 🎯 Advantages of This Setup

### ✅ Supabase Benefits:
- **Free PostgreSQL Database** - 500MB storage
- **Automatic Backups** - Daily backups included
- **Real-time Features** - Can add real-time updates later
- **Built-in Auth** - Could migrate to Supabase Auth later
- **Easy Scaling** - Upgrade when needed
- **Great Dashboard** - Visual database management

### ✅ Hostinger Domain Benefits:
- **Professional Domain** - `yourdomain.com` looks professional
- **Email Included** - Can set up email@yourdomain.com
- **Full Control** - Complete DNS management
- **Affordable** - ~$10-15/year

### ✅ Combined Benefits:
- **Professional Setup** - Custom domain looks great
- **Cost Effective** - Only pay for domain
- **Scalable** - Easy to upgrade later
- **Reliable** - Industry-standard services

---

## 🔄 Alternative: Use Supabase for Everything

If you want to go **fully Supabase**, you'd need to:

1. **Rewrite Backend** to use Supabase client libraries
2. **Use Supabase Auth** instead of Django Auth
3. **Use Supabase Storage** for file uploads
4. **Use Supabase Realtime** for live updates

**Pros:**
- Fully managed backend
- Real-time features built-in
- Less server management

**Cons:**
- Major rewrite required
- Lose Django admin panel
- Different architecture

**Recommendation**: Keep Django backend, use Supabase database. Best of both worlds!

---

## 🐛 Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check Supabase project is active
- Ensure SSL is enabled (`sslmode=require`)

### Domain Not Working
- Wait 24-48 hours for DNS propagation
- Check DNS records in Hostinger
- Verify SSL certificates are active

### CORS Errors
- Update `CORS_ALLOWED_ORIGINS` with your domain
- Check both `yourdomain.com` and `www.yourdomain.com`
- Verify HTTPS is working

### API Not Accessible
- Check `ALLOWED_HOSTS` includes your domain
- Verify subdomain DNS (api.yourdomain.com)
- Check Render custom domain settings

---

## 📝 Final Checklist

- [ ] Supabase database created and connected
- [ ] Django migrations run on Supabase
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Domain purchased on Hostinger
- [ ] DNS records configured
- [ ] SSL certificates active
- [ ] Environment variables updated
- [ ] CORS settings updated
- [ ] Everything tested and working

---

## 🎉 Success!

Your project is now live with:
- ✅ Custom domain (`yourdomain.com`)
- ✅ Professional API subdomain (`api.yourdomain.com`)
- ✅ Supabase database (free tier)
- ✅ HTTPS/SSL enabled
- ✅ Professional setup

**Your URLs:**
- Frontend: `https://yourdomain.com`
- Backend API: `https://api.yourdomain.com`
- API Docs: `https://api.yourdomain.com/`

---

## 🚀 Next Steps (Optional)

1. **Set up email** with Hostinger
2. **Add analytics** (Google Analytics)
3. **Set up monitoring** (Uptime monitoring)
4. **Add CDN** (Cloudflare - free)
5. **Backup strategy** (Supabase has daily backups)

---

**You've got a professional, scalable setup! 🎉**

