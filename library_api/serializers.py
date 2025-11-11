from rest_framework import serializers
from .models import Book, UserProfile, Transaction, PasswordResetCode
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


class BookSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        title = attrs.get('title')
        author = attrs.get('author')
        isbn = attrs.get('isbn')
        published_date = attrs.get('published_date')
        copies_available = attrs.get('copies_available')

        if not title:
            raise serializers.ValidationError('Title is required')
        if not author:
            raise serializers.ValidationError('Author is required')
        if not isbn:
            raise serializers.ValidationError('ISBN is required')
        if not published_date:
            raise serializers.ValidationError('Published date is required')
        if not copies_available:
            raise serializers.ValidationError('There must be more than a single copy available')
        
        return attrs
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'copies_available']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    def validate(self, attrs):
        user = attrs.get('user')
        
        if not user:
            raise serializers.ValidationError('User is required')
        
        return attrs
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'username', 'email', 'role', 'date_of_membership', 'active_status', 'loan_duration']

class TransactionSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), required=False)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.book:
            representation['book'] = BookSerializer(instance.book).data
        return representation

    def is_available(self):
        if self.copies_available >= 1:
            return self.book
        else:
            return serializers.ValidationError(f'{self.title} is not available')
    def borrow(self):
        if self.is_available():
            self.copies_available -= 1
            self.book.save()
        else:
            raise serializers.ValidationError('That book does not have any available copies to check out.')
    
    def validate(self, attrs):
        book = attrs.get('book')
        user = attrs.get('user')
        checkout_date = attrs.get('checkout_date')
        return_date = attrs.get('return_date')
        due_date = attrs.get('due_date')

        if not self.instance:
            if not book:
                raise serializers.ValidationError('Book is required')
            if book.copies_available == 0:
                raise serializers.ValidationError('No copies available for checkout')
        elif book:
            if book.copies_available == 0:
                raise serializers.ValidationError('No copies available for checkout')
        
        return attrs
    
    class Meta:
        model = Transaction
        fields = ['id', 'book', 'user', 'checkout_date', 'return_date', 'due_date', 'overdue_penalty']
        extra_kwargs = {
            'user': {'required': False},
            'checkout_date': {'required': False},
            'due_date': {'required': False},
            'return_date': {'required': False}
        }
        

        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError({'error': 'Both username and password are required'})
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError({'error': 'Invalid username or password'})
        
        if not user.is_active:
            raise serializers.ValidationError({'error': 'User account is disabled'})
        
        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            }

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['is_admin'] = user.is_admin

        return token


# ============================================
# NEW OTP-BASED PASSWORD RESET (SIMPLER APPROACH)
# ============================================

class PasswordResetOTPRequestSerializer(serializers.Serializer):
    """Request OTP code for password reset - much simpler approach"""
    email = serializers.CharField()
    
    def validate_email(self, value):
        """Basic email validation"""
        if not value or not isinstance(value, str):
            raise serializers.ValidationError('Email is required')
        value = value.strip().lower()
        if '@' not in value:
            raise serializers.ValidationError('Please enter a valid email address')
        parts = value.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise serializers.ValidationError('Please enter a valid email address')
        return value
    
    def save(self):
        """Generate and send OTP code"""
        from django.utils import timezone
        from datetime import timedelta
        import random
        import logging
        from django.core.mail import send_mail
        from django.conf import settings
        
        logger = logging.getLogger(__name__)
        email = self.validated_data['email']
        
        # Find user by email
        try:
            user = User.objects.filter(email__iexact=email).first()
        except Exception as e:
            logger.error(f'Error looking up user: {str(e)}')
            return {'email_exists': False}
        
        if not user or not user.email:
            logger.info(f'Password reset requested for non-existent email: {email}')
            return {'email_exists': False}
        
        # Generate 6-digit code
        code = str(random.randint(100000, 999999))
        
        # Set expiration (15 minutes)
        expires_at = timezone.now() + timedelta(minutes=15)
        
        # Invalidate any existing codes for this user
        # This will raise an exception immediately if the table doesn't exist
        from django.db import OperationalError, ProgrammingError
        
        try:
            PasswordResetCode.objects.filter(user=user, used=False).update(used=True)
        except (OperationalError, ProgrammingError) as db_error:
            # Database table doesn't exist or other database error
            error_msg = str(db_error).lower()
            logger.error(f'Database error invalidating codes: {str(db_error)}')
            if 'does not exist' in error_msg or 'relation' in error_msg or 'no such table' in error_msg:
                raise serializers.ValidationError({
                    'email': ['Database migration required. Please run migrations on the server.']
                })
            # Re-raise if it's a different database error
            raise
        except Exception as db_error:
            # Catch any other unexpected errors
            error_msg = str(db_error).lower()
            if 'does not exist' in error_msg or 'relation' in error_msg or 'no such table' in error_msg:
                logger.error(f'Database error (unexpected type): {str(db_error)}')
                raise serializers.ValidationError({
                    'email': ['Database migration required. Please run migrations on the server.']
                })
            # Re-raise if it's not a database error
            raise
        
        # Create new code
        reset_code = None
        try:
            reset_code = PasswordResetCode.objects.create(
                user=user,
                code=code,
                email=email,
                expires_at=expires_at
            )
        except (OperationalError, ProgrammingError) as db_error:
            # Database table doesn't exist or other database error
            error_msg = str(db_error).lower()
            logger.error(f'Database error creating reset code: {str(db_error)}')
            if 'does not exist' in error_msg or 'relation' in error_msg or 'no such table' in error_msg:
                raise serializers.ValidationError({
                    'email': ['Database migration required. Please run migrations on the server.']
                })
            # Re-raise if it's a different database error
            raise
        except Exception as db_error:
            # Catch any other unexpected errors
            error_msg = str(db_error).lower()
            if 'does not exist' in error_msg or 'relation' in error_msg or 'no such table' in error_msg:
                logger.error(f'Database error creating code (unexpected type): {str(db_error)}')
                raise serializers.ValidationError({
                    'email': ['Database migration required. Please run migrations on the server.']
                })
            # Re-raise if it's not a database error
            raise
        
        # Send email
        subject = 'Password Reset Code - Library Management System'
        message = f'''Hello {user.username},

You requested a password reset for your account. Your verification code is:

{code}

This code will expire in 15 minutes.

If you did not request this password reset, please ignore this email.

Best regards,
Library Management System Team
'''
        
        # Get email configuration
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', 'noreply@library.com')
        email_backend = getattr(settings, 'EMAIL_BACKEND', '')
        email_host_user = getattr(settings, 'EMAIL_HOST_USER', '')
        email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        email_host = getattr(settings, 'EMAIL_HOST', '')
        email_port = getattr(settings, 'EMAIL_PORT', '')
        email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
        email_use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
        
        # Log FULL configuration for debugging
        logger.info(f'=== EMAIL CONFIGURATION DEBUG ===')
        logger.info(f'EMAIL_BACKEND: {email_backend}')
        logger.info(f'EMAIL_HOST: {email_host}')
        logger.info(f'EMAIL_PORT: {email_port}')
        logger.info(f'EMAIL_USE_SSL: {email_use_ssl}')
        logger.info(f'EMAIL_USE_TLS: {email_use_tls}')
        logger.info(f'EMAIL_HOST_USER: {email_host_user if email_host_user else "NOT SET"}')
        logger.info(f'EMAIL_HOST_PASSWORD: {"SET (length: " + str(len(email_host_password)) + ")" if email_host_password else "NOT SET"}')
        logger.info(f'DEFAULT_FROM_EMAIL: {from_email}')
        logger.info(f'DEBUG mode: {settings.DEBUG}')
        logger.info(f'================================')
        
        # Validate port
        if email_port:
            if email_use_ssl and email_port not in [465, 994]:
                logger.warning(f'Warning: Using SSL but port is {email_port}. Standard SSL ports are 465 (Gmail) or 994.')
            elif email_use_tls and email_port not in [587, 25]:
                logger.warning(f'Warning: Using TLS but port is {email_port}. Standard TLS port is 587 (Gmail).')
        
        # Check if using console backend in production
        if not settings.DEBUG and 'console' in email_backend.lower():
            error_msg = 'Email configuration error: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set in production. Console backend cannot send real emails.'
            logger.error(error_msg)
            if reset_code:
                try:
                    reset_code.delete()
                except Exception as delete_error:
                    logger.warning(f'Error deleting reset code: {str(delete_error)}')
            raise serializers.ValidationError({'email': [error_msg]})
        
        # Check SMTP credentials if using SMTP
        if 'smtp' in email_backend.lower():
            if not email_host_user or not email_host_password:
                error_msg = 'Email configuration error: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are required for SMTP. Please set these environment variables.'
                logger.error(error_msg)
                if reset_code:
                    try:
                        reset_code.delete()
                    except Exception as delete_error:
                        logger.warning(f'Error deleting reset code: {str(delete_error)}')
                raise serializers.ValidationError({'email': [error_msg]})
        
        try:
            logger.info(f'=== ATTEMPTING TO SEND EMAIL ===')
            logger.info(f'To: {email}')
            logger.info(f'From: {from_email}')
            logger.info(f'Subject: {subject}')
            logger.info(f'Backend: {email_backend}')
            logger.info(f'Host: {email_host}:{email_port}')
            logger.info(f'SSL: {email_use_ssl}, TLS: {email_use_tls}')
            logger.info(f'Timeout: {getattr(settings, "EMAIL_TIMEOUT", "NOT SET")} seconds')
            
            # Import timeout settings
            email_timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
            
            # Use connection with timeout to prevent hanging
            from django.core.mail import get_connection
            connection = get_connection(
                fail_silently=False,
                timeout=email_timeout,
            )
            
            logger.info(f'Connection created with {email_timeout}s timeout')
            
            result = send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,
                connection=connection,
            )
            logger.info(f'✅ EMAIL SENT SUCCESSFULLY!')
            logger.info(f'Result: {result}')
            logger.info(f'OTP code {code} sent to {email}')
            return {'email_exists': True, 'code_sent': True}
        except Exception as e:
            # Log detailed error
            import traceback
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f'Error sending OTP email to {email}')
            logger.error(f'Error type: {error_type}')
            logger.error(f'Error message: {error_msg}')
            logger.error(f'Traceback: {traceback.format_exc()}')
            
            # Provide helpful error message based on error type
            error_lower = error_msg.lower()
            
            if '535' in error_msg or 'authentication failed' in error_lower or 'invalid credentials' in error_lower:
                error_message = 'Email authentication failed. Please check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD. For Gmail, use an App Password.'
            elif '550' in error_msg or 'relay' in error_lower:
                error_message = 'Email server rejected the request. Check if your email account allows SMTP access.'
            elif 'connection' in error_lower or 'timeout' in error_lower or 'network' in error_lower or 'errno' in error_lower or 'gaierror' in error_lower:
                port = getattr(settings, "EMAIL_PORT", "unknown")
                host = getattr(settings, "EMAIL_HOST", "unknown")
                use_ssl = getattr(settings, "EMAIL_USE_SSL", False)
                use_tls = getattr(settings, "EMAIL_USE_TLS", False)
                
                # Provide specific guidance based on port
                if port == 465:
                    error_message = f'Unable to connect to {host}:{port}. Port 465 (SSL) may be blocked. SOLUTION: Update Render environment variables: EMAIL_PORT=587, EMAIL_USE_TLS=True, EMAIL_USE_SSL=False. Then restart the service.'
                elif port == 587:
                    error_message = f'Unable to connect to {host}:{port}. Check: 1) EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct, 2) For Gmail, use an App Password (get from https://myaccount.google.com/apppasswords), 3) Firewall allows port 587.'
                else:
                    error_message = f'Unable to connect to {host}:{port}. For Gmail, use port 587 with TLS: EMAIL_PORT=587, EMAIL_USE_TLS=True, EMAIL_USE_SSL=False.'
            elif 'ssl' in error_lower or 'tls' in error_lower:
                port = getattr(settings, "EMAIL_PORT", "unknown")
                if port == 465:
                    error_message = 'SSL/TLS error with port 465. Try port 587 with TLS instead: EMAIL_PORT=587, EMAIL_USE_TLS=True, EMAIL_USE_SSL=False.'
                else:
                    error_message = 'SSL/TLS connection error. Check EMAIL_USE_TLS and EMAIL_USE_SSL settings. For Gmail with port 587, use: EMAIL_USE_TLS=True, EMAIL_USE_SSL=False.'
            elif 'smtplib' in error_type.lower() or 'smtp' in error_type.lower():
                error_message = f'SMTP error: {error_msg}. Check your email server settings.'
            elif settings.DEBUG:
                error_message = f'Error sending email: {error_msg}. Check server logs for details.'
            else:
                error_message = 'Error sending email. Please check your email configuration and try again later.'
            
            # Delete the code if email failed
            if reset_code:
                try:
                    reset_code.delete()
                except Exception as delete_error:
                    logger.warning(f'Error deleting reset code after email failure: {str(delete_error)}')
            raise serializers.ValidationError({'email': [error_message]})


class PasswordResetOTPVerifySerializer(serializers.Serializer):
    """Verify OTP code and reset password"""
    email = serializers.CharField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    def validate_email(self, value):
        """Normalize email"""
        if not value:
            raise serializers.ValidationError('Email is required')
        return value.strip().lower()
    
    def validate_code(self, value):
        """Validate code format"""
        if not value or len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError('Code must be a 6-digit number')
        return value
    
    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match'})
        return attrs
    
    def save(self):
        """Verify code and reset password"""
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        email = self.validated_data['email']
        code = self.validated_data['code']
        new_password = self.validated_data['new_password']
        
        # Find user
        try:
            user = User.objects.filter(email__iexact=email).first()
        except Exception as e:
            logger.error(f'Error looking up user: {str(e)}')
            raise serializers.ValidationError({'code': ['Invalid code or email']})
        
        if not user:
            raise serializers.ValidationError({'code': ['Invalid code or email']})
        
        # Find valid code
        try:
            reset_code = PasswordResetCode.objects.filter(
                user=user,
                email__iexact=email,
                code=code,
                used=False
            ).first()
        except Exception as e:
            logger.error(f'Error looking up code: {str(e)}')
            raise serializers.ValidationError({'code': ['Invalid code']})
        
        if not reset_code:
            logger.warning(f'Invalid code {code} attempted for {email}')
            raise serializers.ValidationError({'code': ['Invalid or expired code']})
        
        # Check if code is valid
        if not reset_code.is_valid():
            logger.warning(f'Expired code {code} attempted for {email}')
            raise serializers.ValidationError({'code': ['Code has expired. Please request a new one.']})
        
        # Set password
        user.set_password(new_password)
        user.save()
        
        # Mark code as used
        reset_code.used = True
        reset_code.save()
        
        logger.info(f'Password reset successful for {email}')
        return {'success': True, 'message': 'Password has been reset successfully'}


# ============================================
# OLD TOKEN-BASED PASSWORD RESET (KEEP FOR BACKWARD COMPATIBILITY)
# ============================================

class PasswordResetRequestSerializer(serializers.Serializer):
    # Make email field very permissive - accept any string
    email = serializers.CharField()
    
    # Don't validate email format here - handle it in the view/save method
    # This prevents validation errors from blocking legitimate requests

    def save(self):
        email = self.validated_data['email']
        import logging
        logger = logging.getLogger(__name__)
        
        # Normalize email: trim whitespace and convert to lowercase
        email = email.strip() if email else email
        email_lower = email.lower() if email else email
        
        # Find user with exact email match (case-insensitive for email, but exact string match)
        # This ensures only the exact email matches - no partial or similar matches
        # Example: "test@example.com" will match "Test@Example.com" (case-insensitive)
        # But "test@example.com" will NOT match "test123@example.com" (exact match required)
        try:
            # Use case-insensitive exact match (__iexact) which matches exact email regardless of case
            # This is standard email behavior - emails are case-insensitive
            # But __iexact ensures it's an exact match, not a partial match
            user = User.objects.filter(email__iexact=email_lower).first()
            
            if not user:
                logger.info(f'Password reset requested for non-existent email: {email}')
                return {'email_exists': False}
            
            # Verify the user's email exists and is not empty
            if not user.email or user.email.strip() == '':
                logger.warning(f'User {user.username} has no email address set')
                return {'email_exists': False}
            
            # Double-check: compare normalized emails to ensure exact match
            # This prevents any edge cases where database collation might allow partial matches
            user_email_normalized = user.email.strip().lower()
            if user_email_normalized != email_lower:
                logger.warning(f'Email normalization mismatch: user email "{user.email}" normalized to "{user_email_normalized}" does not match requested "{email}" normalized to "{email_lower}"')
                return {'email_exists': False}
                
        except User.MultipleObjectsReturned:
            # Multiple users with same email (shouldn't happen, but handle it)
            logger.error(f'Multiple users found with email: {email}')
            # Still try to get one and proceed
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                return {'email_exists': False}
        except Exception as e:
            # Catch any database errors
            logger.error(f'Error looking up user by email {email}: {str(e)}')
            return {'email_exists': False}
        
        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset URL (frontend URL)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        # Remove trailing slash from frontend_url if present, then add the reset path
        frontend_url = frontend_url.rstrip('/')
        reset_url = f"{frontend_url}/reset-password/{uid}/{token}"
        
        # Send email
        subject = 'Password Reset Request - Library Management System'
        message = f'''Hello {user.username},

You requested a password reset for your account. Please click the link below to reset your password:

{reset_url}

If you did not request this password reset, please ignore this email.

This link will expire in 24 hours.

Best regards,
Library Management System Team
'''
        # Get email configuration
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        email_backend = getattr(settings, 'EMAIL_BACKEND', '')
        email_host_user = getattr(settings, 'EMAIL_HOST_USER', '')
        email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        
        # Log configuration before validation
        logger.info(f'Email configuration check for {email}')
        logger.info(f'  EMAIL_BACKEND: {email_backend}')
        logger.info(f'  EMAIL_HOST_USER: {"SET" if email_host_user else "NOT SET"}')
        logger.info(f'  EMAIL_HOST_PASSWORD: {"SET" if email_host_password else "NOT SET"}')
        logger.info(f'  DEFAULT_FROM_EMAIL: {from_email}')
        
        # Set default from_email if not set
        if not from_email:
            from_email = email_host_user if email_host_user else 'noreply@library.com'
            logger.warning(f'DEFAULT_FROM_EMAIL not set, using: {from_email}')
        
        # Check if using console backend (development)
        if 'console' in email_backend.lower():
            logger.info('Using console email backend - email will be printed to terminal')
            # Don't raise error for console backend, just log it
        elif 'smtp' in email_backend.lower():
            # For SMTP, check if credentials are set
            if not email_host_user or not email_host_password:
                error_msg = 'Email configuration error: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are required for SMTP. Please set these environment variables.'
                logger.error(error_msg)
                raise serializers.ValidationError({'email': [error_msg]})
        
        # Log email details for debugging
        logger.info(f'Attempting to send password reset email to {email}')
        logger.info(f'  Backend: {email_backend}')
        logger.info(f'  From: {from_email}')
        logger.info(f'  To: {email}')
        logger.info(f'  Reset URL: {reset_url}')
        
        # Get timeout settings
        email_timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
        logger.info(f'  Timeout: {email_timeout} seconds')
        
        # Use connection with timeout to prevent hanging
        from django.core.mail import get_connection
        connection = get_connection(
            fail_silently=False,
            timeout=email_timeout,
        )
        logger.info(f'Connection created with {email_timeout}s timeout')
        
        # Check if sending to self (same FROM and TO addresses)
        if from_email and email and from_email.lower().strip() == email.lower().strip():
            logger.info(f'  NOTE: Sending email to self (FROM={from_email}, TO={email})')
            logger.info(f'  Some email providers may have restrictions on sending to yourself')
        
        try:
            # Check if we're in production with console backend (this shouldn't happen)
            if not settings.DEBUG and 'console' in email_backend.lower():
                error_msg = 'Email configuration error: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set in production. Console backend cannot send real emails.'
                logger.error(error_msg)
                raise serializers.ValidationError({'email': [error_msg]})
            
            result = send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,
                connection=connection,
            )
            logger.info(f'✅ Password reset email sent successfully to {email}. Result: {result}')
            
            # In development with console backend, remind about console output
            if 'console' in email_backend.lower():
                logger.warning('NOTE: Email backend is set to console. Email was printed to terminal, not actually sent.')
                # Still return success in development, but log warning
                if settings.DEBUG:
                    logger.info('In production, you must set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to send real emails.')
        except Exception as e:
            # Log detailed error for debugging
            import traceback
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f'Error sending password reset email to {email}')
            logger.error(f'Error type: {error_type}')
            logger.error(f'Error message: {error_msg}')
            logger.error(f'Traceback: {traceback.format_exc()}')
            logger.error(f'Email backend: {email_backend}')
            logger.error(f'From email: {from_email}')
            logger.error(f'EMAIL_HOST_USER set: {bool(email_host_user)}')
            logger.error(f'EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "NOT SET")}')
            logger.error(f'EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "NOT SET")}')
            
            # Provide helpful error message based on error type
            error_lower = error_msg.lower()
            
            if '535' in error_msg or 'authentication failed' in error_lower or 'invalid credentials' in error_lower:
                error_message = 'Email authentication failed. Please check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD. For Gmail, use an App Password.'
            elif '550' in error_msg or 'relay' in error_lower:
                error_message = 'Email server rejected the request. Check if your email account allows SMTP access.'
            elif 'connection' in error_lower or 'timeout' in error_lower or 'network' in error_lower or 'errno' in error_lower or 'gaierror' in error_lower:
                port = getattr(settings, "EMAIL_PORT", "unknown")
                host = getattr(settings, "EMAIL_HOST", "unknown")
                use_ssl = getattr(settings, "EMAIL_USE_SSL", False)
                use_tls = getattr(settings, "EMAIL_USE_TLS", False)
                
                # Provide specific guidance based on port
                if port == 465:
                    error_message = f'Unable to connect to {host}:{port}. Port 465 (SSL) may be blocked. SOLUTION: Update Render environment variables: EMAIL_PORT=587, EMAIL_USE_TLS=True, EMAIL_USE_SSL=False. Then restart the service.'
                elif port == 587:
                    error_message = f'Unable to connect to {host}:{port}. Check: 1) EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct, 2) For Gmail, use an App Password (get from https://myaccount.google.com/apppasswords), 3) Firewall allows port 587.'
                else:
                    error_message = f'Unable to connect to {host}:{port}. For Gmail, use port 587 with TLS: EMAIL_PORT=587, EMAIL_USE_TLS=True, EMAIL_USE_SSL=False.'
            elif 'ssl' in error_lower or 'tls' in error_lower:
                port = getattr(settings, "EMAIL_PORT", "unknown")
                if port == 465:
                    error_message = 'SSL/TLS error with port 465. Try port 587 with TLS instead: EMAIL_PORT=587, EMAIL_USE_TLS=True, EMAIL_USE_SSL=False.'
                else:
                    error_message = 'SSL/TLS connection error. Check EMAIL_USE_TLS and EMAIL_USE_SSL settings. For Gmail with port 587, use: EMAIL_USE_TLS=True, EMAIL_USE_SSL=False.'
            elif 'smtplib' in error_type.lower() or 'smtp' in error_type.lower():
                error_message = f'SMTP error: {error_msg}. Check your email server settings.'
            elif settings.DEBUG:
                error_message = f'Error sending email: {error_msg}. Check server logs for details.'
            else:
                error_message = 'Error sending email. Please check your email configuration and try again later.'
            
            # In debug mode, include more details
            if settings.DEBUG:
                error_message += f' (Error type: {error_type})'
            
            # Raise ValidationError with the error message
            # Use a dict format to ensure proper serialization
            raise serializers.ValidationError({'email': [error_message]})
        
        # Return success with email_exists flag
        return {'email_exists': True, 'user': user}


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )

    def validate_uid(self, value):
        try:
            uid = force_str(urlsafe_base64_decode(value))
            user = User.objects.get(pk=uid)
            self.user = user
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Invalid reset link')
        return value

    def validate(self, attrs):
        # Validate password match
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match'})
        
        # Validate uid and token - ensure user is set first
        if not hasattr(self, 'user'):
            raise serializers.ValidationError({'uid': 'Invalid reset link'})
        
        # Validate token
        token = attrs.get('token')
        if not default_token_generator.check_token(self.user, token):
            raise serializers.ValidationError({'token': 'Invalid or expired reset link'})
        
        return attrs

    def save(self):
        user = self.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user