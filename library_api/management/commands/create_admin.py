"""
Secure management command to create/update superuser from environment variables.
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates or updates a superuser from environment variables (ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME')
        email = os.getenv('ADMIN_EMAIL', '')
        password = os.getenv('ADMIN_PASSWORD')

        if not username or not password:
            self.stdout.write(
                self.style.ERROR(
                    'Error: ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required.'
                )
            )
            self.stdout.write(
                'Set these in Render Dashboard → Environment Variables'
            )
            return

        try:
            user, created = User.objects.get_or_create(username=username)
            
            if created:
                # New user - create as superuser
                user.is_superuser = True
                user.is_staff = True
                user.email = email
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser "{username}"')
                )
            else:
                # Existing user - update credentials
                user.is_superuser = True
                user.is_staff = True
                if email:
                    user.email = email
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated superuser "{username}"')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating/updating superuser: {str(e)}')
            )

