"""
WSGI config for library_management_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import logging

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_system.settings')

from django.core.wsgi import get_wsgi_application

# Initialize Django application
application = get_wsgi_application()

# Auto-run migrations on startup if table is missing (AFTER Django is initialized)
try:
    # Only check in production (not in test/debug)
    if os.getenv('DEBUG', 'False').lower() != 'true':
        from django.db import connection
        from django.core.management import call_command
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'library_api_passwordresetcode'
                );
            """)
            table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            logger.warning("⚠️  PasswordResetCode table missing! Running migrations on startup...")
            try:
                call_command('migrate', '--noinput', verbosity=1)
                logger.info("✅ Migrations completed on startup!")
            except Exception as migrate_error:
                logger.error(f"❌ Failed to run migrations on startup: {str(migrate_error)}")
                logger.info("💡 You can run migrations manually via: POST https://api.librarymanagementsystem.store/migrate/")
        else:
            logger.info("✅ Database tables are up to date.")
except Exception as e:
    # Don't fail startup if migration check fails
    logger.warning(f"⚠️  Could not check/run migrations on startup: {str(e)}")
    logger.info("💡 You can run migrations manually via: POST https://api.librarymanagementsystem.store/migrate/")
