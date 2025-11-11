# Password Reset OTP System - Logic, Flow & Setup Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [How It Works (Logic & Flow)](#how-it-works-logic--flow)
3. [What You Need to Do](#what-you-need-to-do)
4. [Testing the System](#testing-the-system)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

The password reset system uses **OTP (One-Time Password) codes** instead of complex URL tokens. This makes it:
- ✅ Simpler to implement
- ✅ More reliable (no URL parsing issues)
- ✅ Mobile-friendly
- ✅ Easier to debug

---

## 🔄 How It Works (Logic & Flow)

### Step-by-Step Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER FLOW                                 │
└─────────────────────────────────────────────────────────────┘

1. User clicks "Forgot Password" on login page
   ↓
2. User enters email address
   ↓
3. Frontend sends: POST /api/password-reset-otp/ { email }
   ↓
4. Backend:
   - Validates email format
   - Checks if user exists in database
   - Generates random 6-digit code (100000-999999)
   - Stores code in PasswordResetCode table with:
     * user (ForeignKey)
     * code (6 digits)
     * email
     * expires_at (15 minutes from now)
     * used (False)
   - Invalidates any previous unused codes for this user
   - Sends email with code
   ↓
5. User receives email with 6-digit code
   ↓
6. User enters code + new password + confirm password
   ↓
7. Frontend sends: POST /api/password-reset-otp-verify/
   {
     email: "user@example.com",
     code: "123456",
     new_password: "newpass123",
     new_password_confirm: "newpass123"
   }
   ↓
8. Backend:
   - Validates email format
   - Validates code is 6 digits
   - Validates passwords match and are at least 8 characters
   - Looks up PasswordResetCode record:
     * Matches user + email + code
     * Checks code is not used
     * Checks code is not expired (expires_at > now)
   - If valid:
     * Sets new password for user
     * Marks code as used (used = True)
     * Returns success
   - If invalid:
     * Returns error message
   ↓
9. User redirected to login page
   ↓
10. User logs in with new password
```

### Database Logic

**PasswordResetCode Model:**
```python
- user: Links to User who requested reset
- code: 6-digit numeric code
- email: Email address used
- created_at: When code was generated
- expires_at: created_at + 15 minutes
- used: Boolean (True after successful reset)
```

**Code Validation Logic:**
1. Code must exist in database
2. Code must match user + email
3. Code must not be used (used = False)
4. Code must not be expired (expires_at > current_time)

**Security Features:**
- Codes expire after 15 minutes
- Codes can only be used once
- New codes invalidate previous unused codes
- Email must match the one used to request code

---

## ✅ What You Need to Do

### 1. Environment Variables Setup

Make sure these are set in your `.env` file or production environment:

```bash
# Email Configuration (REQUIRED for production)
# NOTE: EMAIL_BACKEND is OPTIONAL - it auto-detects based on credentials below
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend  # Optional - auto-detected
EMAIL_HOST=smtp.gmail.com  # or your SMTP server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com  # REQUIRED for production
EMAIL_HOST_PASSWORD=your-app-password  # REQUIRED for production (For Gmail, use App Password)
DEFAULT_FROM_EMAIL=your-email@gmail.com  # Optional - defaults to EMAIL_HOST_USER

# Frontend URL (for email links if needed)
FRONTEND_URL=https://yourdomain.com
```

**Important:** 
- ✅ **You DON'T need to set `EMAIL_BACKEND`** - it auto-detects:
  - If `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set → Uses SMTP backend
  - If they're NOT set → Uses console backend (emails print to terminal)
- ✅ **You MUST set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`** for production
- ✅ Setting `EMAIL_BACKEND` explicitly is optional (only if you want to override auto-detection)

**For Gmail:**
1. Enable 2-Step Verification
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password)

### 2. Database Migration

The migration should already be applied, but if not:

```bash
python manage.py migrate
```

This creates the `PasswordResetCode` table.

### 3. Test Email Configuration

Test that emails are sending correctly:

```bash
# In Django shell
python manage.py shell

>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### 4. Frontend Configuration

The frontend is already configured. Just make sure:

- ✅ `frontend/src/pages/ResetPasswordOTP.jsx` exists
- ✅ `frontend/src/App.jsx` has the route: `/forgot-password`
- ✅ `frontend/src/contexts/AuthContext.jsx` has `verifyOTPAndResetPassword` function

### 5. Production Deployment Checklist

- [ ] Environment variables set in production (Render, Heroku, etc.)
- [ ] Database migration applied
- [ ] Email credentials are correct
- [ ] Test password reset flow end-to-end
- [ ] Check email delivery (spam folder)
- [ ] Monitor logs for errors

---

## 🧪 Testing the System

### Manual Testing Steps

1. **Test Email Request:**
   ```
   - Go to /forgot-password
   - Enter a valid email address
   - Click "Send Verification Code"
   - Check email inbox (and spam folder)
   - Verify you received a 6-digit code
   ```

2. **Test Code Verification:**
   ```
   - Enter the 6-digit code from email
   - Enter new password (min 8 characters)
   - Confirm password
   - Click "Reset Password"
   - Should redirect to login page
   ```

3. **Test Invalid Scenarios:**
   ```
   - Wrong email → Should show "No account found"
   - Wrong code → Should show "Invalid or expired code"
   - Expired code (wait 15+ minutes) → Should show "Code expired"
   - Mismatched passwords → Should show "Passwords do not match"
   ```

### API Testing (Using curl)

**Request OTP:**
```bash
curl -X POST http://localhost:8000/api/password-reset-otp/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**Verify and Reset:**
```bash
curl -X POST http://localhost:8000/api/password-reset-otp-verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
  }'
```

---

## 🔧 Troubleshooting

### Problem: Code Not Received

**Check:**
1. Email spam/junk folder
2. Email configuration in settings
3. Server logs for email errors
4. SMTP credentials are correct

**Solution:**
```python
# Check email backend in Django shell
from django.conf import settings
print(settings.EMAIL_BACKEND)
print(settings.EMAIL_HOST)
print(settings.EMAIL_HOST_USER)
```

### Problem: "Invalid or Expired Code"

**Possible Causes:**
- Code expired (15 minutes passed)
- Code already used
- Wrong email address
- Code format incorrect (must be 6 digits)

**Solution:**
- Request a new code
- Ensure email matches exactly
- Check code is exactly 6 digits

### Problem: Email Sending Fails

**Check:**
1. `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set (REQUIRED)
2. For Gmail: Using App Password (not regular password)
3. `EMAIL_HOST` and `EMAIL_PORT` are correct
4. `EMAIL_USE_TLS` or `EMAIL_USE_SSL` is set correctly
5. `EMAIL_BACKEND` is NOT required - it auto-detects, but you can set it explicitly if needed

**Gmail Setup:**
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Use the 16-character App Password

### Problem: Database Errors

**Check:**
```bash
# Verify migration was applied
python manage.py showmigrations library_api

# Should show:
# [X] 0012_passwordresetcode
```

**If migration missing:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📊 Code Flow Diagram

```
┌─────────────┐
│   Frontend  │
│  Component  │
└──────┬──────┘
       │
       │ 1. User enters email
       ↓
┌──────────────────────┐
│  POST /password-     │
│  reset-otp/          │
│  { email }           │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Backend View         │
│  PasswordResetOTP     │
│  RequestView          │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Serializer           │
│  PasswordResetOTP     │
│  RequestSerializer   │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Generate 6-digit     │
│  code & save to DB    │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Send Email          │
│  with code           │
└──────┬───────────────┘
       │
       ↓
┌─────────────┐
│   User      │
│  Receives   │
│   Email     │
└──────┬──────┘
       │
       │ 2. User enters code + password
       ↓
┌──────────────────────┐
│  POST /password-     │
│  reset-otp-verify/   │
│  { email, code,      │
│    new_password,     │
│    confirm }          │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Backend View         │
│  PasswordResetOTP     │
│  VerifyView           │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Serializer           │
│  PasswordResetOTP     │
│  VerifySerializer     │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Validate code:       │
│  - Exists in DB       │
│  - Not expired        │
│  - Not used           │
│  - Matches user       │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Set new password     │
│  Mark code as used    │
└──────┬───────────────┘
       │
       ↓
┌─────────────┐
│   Success   │
│  Redirect   │
│  to Login   │
└─────────────┘
```

---

## 🎯 Key Points to Remember

1. **Codes expire in 15 minutes** - User must use code quickly
2. **Codes are one-time use** - Once used, cannot be reused
3. **New codes invalidate old ones** - Only latest code is valid
4. **Email must match exactly** - Case-insensitive but must be same email
5. **Password minimum 8 characters** - Enforced on both frontend and backend

---

## 📝 Quick Reference

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/password-reset-otp/` | POST | Request OTP code |
| `/api/password-reset-otp-verify/` | POST | Verify code and reset password |

### Request/Response Examples

**Request OTP:**
```json
POST /api/password-reset-otp/
{
  "email": "user@example.com"
}
```

**Verify OTP:**
```json
POST /api/password-reset-otp-verify/
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "newpass123",
  "new_password_confirm": "newpass123"
}
```

### Database Queries (for debugging)

```python
# Check codes for a user
from library_api.models import PasswordResetCode
from django.contrib.auth.models import User

user = User.objects.get(email='user@example.com')
codes = PasswordResetCode.objects.filter(user=user).order_by('-created_at')
for code in codes:
    print(f"Code: {code.code}, Used: {code.used}, Expires: {code.expires_at}")

# Clean up expired codes
from django.utils import timezone
PasswordResetCode.objects.filter(expires_at__lt=timezone.now()).delete()
```

---

## 🚀 Next Steps

1. ✅ **Set up email configuration** (if not done)
2. ✅ **Test the flow** end-to-end
3. ✅ **Deploy to production** with correct environment variables
4. ✅ **Monitor logs** for any issues
5. ✅ **Test with real users** before going live

---

**Last Updated:** November 2025  
**Version:** 1.0

For detailed API documentation, see `PASSWORD_RESET_OTP_GUIDE.md`

