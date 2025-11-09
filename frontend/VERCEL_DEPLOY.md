# 🚀 Vercel Deployment Guide - Fix 404 Errors

## ✅ Fixed Configuration

The `vercel.json` is now correctly configured for React SPA routing.

## 🔧 Vercel Project Settings

**CRITICAL: Set these in Vercel Dashboard:**

1. **Root Directory:** `frontend` ⚠️ **MUST BE SET**
2. **Framework Preset:** Vite (auto-detected)
3. **Build Command:** `npm run build` (auto)
4. **Output Directory:** `dist` (auto)
5. **Install Command:** `npm install` (auto)

## 📋 Step-by-Step Deployment

### 1. Go to Vercel Dashboard
- Visit: https://vercel.com/dashboard
- Click "Add New Project"

### 2. Import Your Repository
- Connect your GitHub/GitLab/Bitbucket
- Select your repository

### 3. Configure Project Settings
**IMPORTANT:** Click "Edit" next to "Root Directory"
- Set to: `frontend`
- This tells Vercel where your frontend code is

### 4. Environment Variables (Optional)
If you want to override the API URL:
- Name: `VITE_API_URL`
- Value: `https://library-management-system-api-of7r.onrender.com/api`

**Note:** The backend URL is already hardcoded, so this is optional.

### 5. Deploy
- Click "Deploy"
- Wait for build to complete

## 🔍 Troubleshooting 404 Errors

### If you still get 404s:

1. **Check Root Directory:**
   - Vercel Dashboard → Settings → General
   - Root Directory MUST be: `frontend`

2. **Check Build Logs:**
   - Vercel Dashboard → Deployments → Click on latest deployment
   - Check if build succeeded
   - Look for errors in the build output

3. **Verify Build Output:**
   - Build should create `dist/` folder
   - Should contain `index.html` and `assets/` folder

4. **Check Network Tab:**
   - Open browser DevTools → Network
   - See if files are loading (404 on specific files?)
   - Check if API calls are going to correct backend

## ✅ What Should Work After Deployment

- ✅ All React routes (`/`, `/login`, `/dashboard`, etc.)
- ✅ API calls to Render backend
- ✅ Static assets (CSS, JS, images)

## 🐛 Common Issues

### Issue: "404 on all routes"
**Solution:** Root Directory not set to `frontend`

### Issue: "404 on assets"
**Solution:** Check if build created `dist/assets/` folder

### Issue: "API calls failing"
**Solution:** Check CORS on backend (already configured to allow all origins)

### Issue: "Blank page"
**Solution:** Check browser console for JavaScript errors

## 📝 Quick Checklist

- [ ] Root Directory set to `frontend` in Vercel
- [ ] Build completed successfully
- [ ] `dist/` folder created with `index.html`
- [ ] Backend URL is correct in `src/services/api.js`
- [ ] CORS allows all origins on backend

---

**The configuration is ready! Just make sure Root Directory is set to `frontend` in Vercel! 🎯**

