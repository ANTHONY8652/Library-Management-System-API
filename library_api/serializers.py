from rest_framework import serializers
from .models import Book, UserProfile, Transaction
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
            raise serializers.validationError({'error': 'User accpunt is disabled'})
        
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


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            pass
        return value

    def save(self):
        email = self.validated_data['email']
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Log for debugging in development
            logger.info(f'Password reset requested for non-existent email: {email}')
            # Return a special marker to indicate email doesn't exist
            # This allows frontend to show signup link
            return {'email_exists': False}
        
        # Check if user has an email address
        if not user.email:
            logger.warning(f'User {user.username} has no email address set')
            # Return marker indicating issue
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
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@library.com')
        
        # Log email details for debugging
        email_backend = getattr(settings, 'EMAIL_BACKEND', '')
        logger.info(f'Attempting to send password reset email to {email} using backend: {email_backend}')
        logger.info(f'Reset URL: {reset_url}')
        
        try:
            result = send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,
            )
            logger.info(f'Password reset email sent successfully to {email}. Result: {result}')
            # In development with console backend, remind about console output
            if 'console' in email_backend.lower():
                logger.info('NOTE: Email backend is set to console. Check your Django server console/terminal for the email content.')
        except Exception as e:
            # Log detailed error for debugging
            import traceback
            logger.error(f'Error sending password reset email to {email}: {str(e)}')
            logger.error(f'Traceback: {traceback.format_exc()}')
            # In development, include more details
            if settings.DEBUG:
                raise serializers.ValidationError(f'Error sending email: {str(e)}. Check server logs for details.')
            else:
                raise serializers.ValidationError('Error sending email. Please try again later.')
        
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