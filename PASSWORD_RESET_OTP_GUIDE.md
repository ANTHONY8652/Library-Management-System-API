# Password Reset OTP System - Complete Guide

## Overview

This guide explains the new **OTP (One-Time Password) based password reset system** implemented for the Library Management System. This approach is simpler, more reliable, and user-friendly compared to the token-based system.

## How It Works

### Flow Diagram

```
1. User enters email → Request OTP code
2. System generates 6-digit code → Sends via email
3. User enters code + new password → Password reset
```

### Key Features

- ✅ **6-digit numeric codes** - Easy to enter
- ✅ **15-minute expiration** - Security with convenience
- ✅ **One-time use** - Codes are invalidated after use
- ✅ **Mobile-friendly** - No complex URL parsing
- ✅ **Simple validation** - No token encoding/decoding issues

## Backend Implementation

### Database Model

**Model:** `PasswordResetCode` (in `library_api/models.py`)

```python
- user: ForeignKey to User
- code: CharField (6 digits)
- email: EmailField
- created_at: DateTimeField
- expires_at: DateTimeField
- used: BooleanField
```

### API Endpoints

#### 1. Request OTP Code

**Endpoint:** `POST /api/password-reset-otp/`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "A 6-digit verification code has been sent to your email address.",
  "email_exists": true,
  "success": true
}
```

**Email Not Found (200):**
```json
{
  "message": "No account found with this email address.",
  "email_exists": false,
  "suggest_signup": true,
  "success": true
}
```

**Error Response (400):**
```json
{
  "error": "Invalid email address.",
  "success": false,
  "errors": {...}
}
```

#### 2. Verify OTP and Reset Password

**Endpoint:** `POST /api/password-reset-otp-verify/`

**Request:**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Success Response (200):**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password.",
  "success": true
}
```

**Error Response (400):**
```json
{
  "error": "Invalid or expired code. Please request a new code.",
  "success": false
}
```

### Code Generation

- **Format:** 6-digit numeric code (100000-999999)
- **Expiration:** 15 minutes from creation
- **Invalidation:** Previous unused codes for the same user are marked as used when a new code is generated

## Frontend Implementation

### Components

1. **ResetPasswordOTP.jsx** - Main component with two steps:
   - Step 1: Email entry
   - Step 2: Code + password entry

2. **AuthContext.jsx** - Updated with:
   - `requestPasswordReset()` - Requests OTP code
   - `verifyOTPAndResetPassword()` - Verifies code and resets password

### Routes

- `/forgot-password` - Uses the new OTP system
- `/reset-password/:uid/:token` - Old token-based system (kept for backward compatibility)

## Setup Instructions

### 1. Run Database Migration

```bash
python manage.py migrate
```

This creates the `PasswordResetCode` table.

### 2. Configure Email Settings

Ensure your email settings are configured in `settings.py` or environment variables:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

### 3. Test the System

1. **Request OTP:**
   ```bash
   curl -X POST http://localhost:8000/api/password-reset-otp/ \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
   ```

2. **Check email** for the 6-digit code

3. **Verify and Reset:**
   ```bash
   curl -X POST http://localhost:8000/api/password-reset-otp-verify/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "code": "123456",
       "new_password": "newpass123",
       "new_password_confirm": "newpass123"
     }'
   ```

## Email Template

The system sends a simple email with:

```
Subject: Password Reset Code - Library Management System

Hello [username],

You requested a password reset for your account. Your verification code is:

[6-digit code]

This code will expire in 15 minutes.

If you did not request this password reset, please ignore this email.

Best regards,
Library Management System Team
```

## Security Features

1. **Code Expiration:** Codes expire after 15 minutes
2. **One-Time Use:** Codes are marked as used after successful password reset
3. **Automatic Invalidation:** New codes invalidate previous unused codes
4. **Email Validation:** Only valid email addresses are accepted
5. **Password Requirements:** Minimum 8 characters, must match confirmation

## Troubleshooting

### Code Not Received

1. **Check email spam folder**
2. **Verify email configuration** in settings
3. **Check server logs** for email sending errors
4. **Ensure SMTP credentials are correct**

### "Invalid or Expired Code" Error

1. **Code expired** - Request a new code (15-minute limit)
2. **Code already used** - Request a new code
3. **Wrong email** - Ensure email matches the one used to request code
4. **Code format** - Must be exactly 6 digits

### Email Sending Fails

1. **Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD** are set
2. **For Gmail:** Use an App Password, not your regular password
3. **Check EMAIL_HOST and EMAIL_PORT** are correct
4. **Verify EMAIL_USE_TLS or EMAIL_USE_SSL** settings

## Migration from Token-Based System

The old token-based system (`/api/password-reset/` and `/api/password-reset-confirm/`) is still available for backward compatibility but is **deprecated**. 

**Recommended:** Use the new OTP system for all new implementations.

## Frontend Integration Example

```javascript
// Request OTP
const result = await requestPasswordReset('user@example.com')
if (result.success) {
  // Show code entry form
}

// Verify and reset
const resetResult = await verifyOTPAndResetPassword(
  'user@example.com',
  '123456',
  'newpassword123',
  'newpassword123'
)
if (resetResult.success) {
  // Redirect to login
}
```

## API Error Codes

| Status Code | Meaning |
|------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input, expired code, etc.) |
| 500 | Server Error (email sending failure, database error) |

## Best Practices

1. **Rate Limiting:** Consider adding rate limiting to prevent abuse
2. **Code Cleanup:** Periodically clean up expired codes from database
3. **Logging:** Monitor failed attempts for security
4. **User Feedback:** Provide clear error messages
5. **Email Delivery:** Use a reliable email service (SendGrid, AWS SES, etc.)

## Database Cleanup

To clean up expired codes (run periodically):

```python
from django.utils import timezone
from library_api.models import PasswordResetCode

# Delete codes older than 24 hours
PasswordResetCode.objects.filter(
    expires_at__lt=timezone.now() - timedelta(hours=24)
).delete()
```

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Verify email configuration
3. Test with a known working email account
4. Check database for code records

---

**Last Updated:** November 2025
**Version:** 1.0

