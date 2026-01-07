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
            'user': {'required': False, 'read_only': True},
            'checkout_date': {'required': False},
            'due_date': {'required': False},
            'return_date': {'required': False}
        }
        

        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True},
        }
    
    def validate_username(self, value):
        """Normalize username: trim whitespace, preserve original case for display"""
        if not value:
            raise serializers.ValidationError('Username is required')
        # Allow spaces in username, but trim leading/trailing spaces
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Username cannot be empty')
        # Check length
        if len(value) < 3:
            raise serializers.ValidationError('Username must be at least 3 characters long')
        if len(value) > 150:
            raise serializers.ValidationError('Username must be less than 150 characters')
        return value
    
    def validate_email(self, value):
        """Normalize email: trim and lowercase"""
        if not value:
            raise serializers.ValidationError('Email is required')
        return value.strip().lower()
    
    def validate(self, attrs):
        """Check for duplicate usernames (case-insensitive) and emails"""
        username = attrs.get('username', '').strip()
        email = attrs.get('email', '').strip().lower()
        
        # Check for existing username (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({
                'username': 'A user with this username already exists.'
            })
        
        # Check for existing email (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({
                'email': 'A user with this email already exists.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create user with normalized email"""
        # Store username as-is (allows spaces and original case)
        # Store email in lowercase
        user = User.objects.create_user(
            username=validated_data['username'].strip(),
            email=validated_data['email'].strip().lower(),
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(help_text='Username or email address')
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password')

        if not username_or_email or not password:
            raise serializers.ValidationError({'error': 'Both username/email and password are required'})
        
        # Try to find user by username (case-insensitive) or email (case-insensitive)
        user = None
        
        # Check if it looks like an email (contains @)
        if '@' in username_or_email:
            # Try to find by email (case-insensitive)
            try:
                user = User.objects.get(email__iexact=username_or_email.lower())
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # If multiple users with same email, get the first one
                user = User.objects.filter(email__iexact=username_or_email.lower()).first()
        else:
            # Try to find by username (case-insensitive)
            try:
                user = User.objects.get(username__iexact=username_or_email)
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                # If multiple users with same username (shouldn't happen), get the first one
                user = User.objects.filter(username__iexact=username_or_email).first()
        
        # If user found, authenticate with password
        if user:
            user = authenticate(username=user.username, password=password)
        
        if not user:
            raise serializers.ValidationError({'error': 'Invalid username/email or password'})
        
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
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@library.com')
        email_backend = getattr(settings, 'EMAIL_BACKEND', '')
        
        # Check email backend configuration
        if not settings.DEBUG and 'console' in email_backend.lower():
            if reset_code:
                reset_code.delete()
            raise serializers.ValidationError({
                'email': ['Email configuration error: Email service not configured properly. Please contact administrator.']
            })
        
        # Send email using Django's send_mail (will use configured backend)
        try:
            email_timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
            from django.core.mail import get_connection
            connection = get_connection(fail_silently=False, timeout=email_timeout)
            
            result = send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,
                connection=connection,
            )
            
            logger.info(f'Password reset OTP sent to {email}')
            return {'email_exists': True, 'code_sent': True}
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            error_lower = error_msg.lower()
            
            logger.error(f'Error sending password reset email: {error_type}: {error_msg}')
            
            # Provide user-friendly error messages
            if 'api' in email_backend.lower() or 'brevo' in email_backend.lower():
                if '401' in error_msg or 'unauthorized' in error_lower:
                    error_message = 'Email service authentication failed. Please check BREVO_API_KEY configuration.'
                elif '400' in error_msg:
                    error_message = 'Email service configuration error. Please check DEFAULT_FROM_EMAIL and sender verification.'
                else:
                    error_message = 'Error sending email. Please try again later or contact administrator.'
            elif 'connection' in error_lower or 'timeout' in error_lower:
                error_message = 'Unable to connect to email service. This may be a temporary issue. Please try again later.'
            elif 'authentication' in error_lower or '535' in error_msg:
                error_message = 'Email authentication failed. Please contact administrator.'
            else:
                error_message = 'Error sending email. Please try again later.'
            
            # Delete the code if email failed
            if reset_code:
                try:
                    reset_code.delete()
                except Exception:
                    pass
            
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
        
        if not reset_code or not reset_code.is_valid():
            raise serializers.ValidationError({'code': ['Invalid or expired code']})
        
        # Set password and mark code as used
        user.set_password(new_password)
        user.save()
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
        email = email.strip().lower()
        
        try:
            user = User.objects.filter(email__iexact=email).first()
            if not user or not user.email:
                return {'email_exists': False}
        except Exception as e:
            logger.error(f'Error looking up user: {str(e)}')
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
        
        # Set default from_email if not set
        if not from_email:
            from_email = email_host_user if email_host_user else 'noreply@library.com'
        
        # Check email backend configuration
        if not settings.DEBUG and 'console' in email_backend.lower():
            raise serializers.ValidationError({
                'email': ['Email configuration error: Email service not configured properly. Please contact administrator.']
            })
        
        if 'smtp' in email_backend.lower() and (not email_host_user or not email_host_password):
            raise serializers.ValidationError({
                'email': ['Email configuration error: Email service not configured properly. Please contact administrator.']
            })
        
        # Send email
        email_timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
        from django.core.mail import get_connection
        connection = get_connection(fail_silently=False, timeout=email_timeout)
        
        try:
            send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,
                connection=connection,
            )
            logger.info(f'Password reset email sent to {email}')
        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            logger.error(f'Error sending password reset email: {type(e).__name__}')
            
            # Provide user-friendly error message
            if 'authentication' in error_lower or '535' in error_msg:
                error_message = 'Email authentication failed. Please contact administrator.'
            elif 'connection' in error_lower or 'timeout' in error_lower:
                error_message = 'Unable to connect to email service. Please try again later.'
            elif settings.DEBUG:
                error_message = f'Error sending email: {error_msg}'
            else:
                error_message = 'Error sending email. Please try again later.'
            
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
