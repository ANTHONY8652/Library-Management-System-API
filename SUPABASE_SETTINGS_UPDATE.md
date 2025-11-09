# 🔧 Supabase Database Configuration for Django

This file shows the exact code changes needed to use Supabase PostgreSQL with your Django project.

## Update `library_management_system/settings.py`

### Option 1: Use Supabase Connection String (Recommended)

Replace your current `DATABASES` configuration with:

```python
import os
from urllib.parse import urlparse

# Supabase Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')  # From Supabase dashboard

if DATABASE_URL:
    # Parse the Supabase connection string
    db_info = urlparse(DATABASE_URL)
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_info.path[1:] if db_info.path.startswith('/') else db_info.path,  # Remove leading '/'
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
    # Fallback to individual environment variables (for local dev)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv("DB_NAME", "library_db"),
            'USER': os.getenv("DB_USER", "postgres"),
            'PASSWORD': os.getenv("DB_PASSWORD", ""),
            'HOST': os.getenv("DB_HOST", "localhost"),
            'PORT': os.getenv("DB_PORT", "5432"),
        }
    }
```

### Option 2: Use Individual Environment Variables

If you prefer to set individual variables:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),  # From Supabase: db.xxxxx.supabase.co
        'PORT': os.getenv("DB_PORT", "5432"),
        'OPTIONS': {
            'sslmode': 'require',  # Required for Supabase
        },
    }
}
```

## Environment Variables for Render

When deploying to Render, add these environment variables:

```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

OR individually:

```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=<your-supabase-password>
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
```

## Getting Supabase Connection String

1. Go to Supabase Dashboard
2. Click **Settings** → **Database**
3. Scroll to **"Connection string"**
4. Copy the **"URI"** format
5. Replace `[YOUR-PASSWORD]` with your actual database password

## Testing Locally

1. Set environment variable:
   ```bash
   export DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Test connection:
   ```bash
   python manage.py dbshell
   ```

## Important Notes

- ✅ Supabase requires SSL (`sslmode=require`)
- ✅ Use connection pooling for production (Supabase provides this)
- ✅ Free tier: 500MB database, 2GB bandwidth
- ✅ Daily automatic backups included
- ✅ Can upgrade to Pro plan ($25/month) for more resources

