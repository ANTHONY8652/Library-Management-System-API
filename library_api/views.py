from rest_framework import filters, permissions, generics, serializers, status
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from .models import Book, Transaction, UserProfile
from .serializers import BookSerializer, TransactionSerializer, UserProfileSerializer, UserRegistrationSerializer, UserLoginSerializer, TokenObtainPairSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .permissions import IsAdminUser, IsMemberUser, CanDeleteBook, CanViewBook, IsAdminOrMember
from django.shortcuts import render
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
        })

class MyCursorPagination(CursorPagination):
    page_size = 10
    ordering = 'published_date'

class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['title', 'published_date']
    
    def get_queryset(self):
        try:
            return Book.objects.all().order_by('title', 'author')
        except Exception as e:
            logger.error(f"Error fetching books: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            try:
                return Book.objects.none()
            except:
                return []
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in BookListCreateView.list: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': 'Internal server error',
                'message': 'Unable to fetch books. Please check database connection.',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    permission_classes = [CanViewBook]
    
    def get_queryset(self):
        try:
            return Book.objects.all()
        except Exception as e:
            logger.error(f"Error in BookDetailView.get_queryset: {str(e)}")
            return Book.objects.none()

    def perform_destroy(self, instance):
        if instance.copies_available <= 0:
            raise serializers.ValidationError('You cannot delete a book that has no copies currently available')
        logger.debug(f'Book {instance.title} deleted by {self.request.user.username}')

        instance.delete()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            role = 'member'
            try:
                role = user.userprofile.role
            except:
                pass
            
            refresh = RefreshToken.for_user(user)

            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': role,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': f'{user} created successfully.Redirecting to login...',
                'redirect_url': 'http://localhost:8000/login/',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all().order_by('user')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminUser, permissions.IsAuthenticated]

class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrMember]

class CheckOutBookView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]

    def perform_create(self, serializer):
        book = serializer.validated_data.get('book')
        if not book:
            raise serializers.ValidationError('Book is required')
        
        if book.copies_available > 0:
            try:
                if self.request.user.userprofile.has_outstanding_transactions(book):
                    raise serializers.ValidationError('You already have an outstanding transaction for this book')
            except Exception as e:
                logger.error(f'Error checking outstanding transactions: {e}')
            
            book.copies_available -= 1
            book.save()
            
            try:
                user_profile = self.request.user.userprofile
                loan_days = 30 if user_profile.role == 'admin' else 14
            except:
                loan_days = 14
                logger.warning(f'UserProfile not found for user {self.request.user.username}, using default loan duration')
            
            due_date = timezone.now().date() + timedelta(days=loan_days)
            checkout_date = serializer.validated_data.get('checkout_date') or timezone.now().date()
            
            serializer.save(
                user=self.request.user,
                checkout_date=checkout_date,
                due_date=due_date,
                return_date=None
            )
        else:
            raise serializers.ValidationError('No copies available for checkout')

class ReturnBookview(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]

    def perform_update(self, serializer):
        transaction = serializer.instance
        if transaction.return_date is not None:
            raise serializers.ValidationError('This book has already been returned.')
        
        if transaction.user != self.request.user:
            raise serializers.ValidationError('You are not authorized to return this book.')
        
        transaction.return_date = timezone.now().date()
        transaction.book.copies_available += 1
        transaction.book.save()
        transaction.calculate_penalty()
        serializer.save()

class MyBooksView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Transaction.objects.filter(
            return_date__isnull=True,
            user=self.request.user
        ).select_related('book').order_by('-checkout_date')

class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).select_related('book').order_by('-checkout_date')

class CurrentUserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.userprofile

class OverdueBooksView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Transaction.objects.filter(return_date__isnull=True, due_date__lt=timezone.now().date(), user=self.request.user)

class BookFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = filters.CharFilter(field_name='author', lookup_expr='icontains')
    isbn = filters.CharFilter(field_name='isbn', lookup_expr='icontains')
    search = filters.CharFilter(method='filter_search', label='Search')
    available = filters.BooleanFilter(field_name='copies_available', lookup_expr='gt', method='filter_available')
    published_after = filters.DateFilter(field_name='published_date', lookup_expr='gte')
    published_before = filters.DateFilter(field_name='published_date', lookup_expr='lte')
    year_published = filters.NumberFilter(field_name='published_date', lookup_expr='year')

    def filter_search(self, queryset, name, value):
        """Unified search across title, author, and ISBN"""
        if not value:
            return queryset
        from django.db.models import Q
        return queryset.filter(
            Q(title__icontains=value) |
            Q(author__icontains=value) |
            Q(isbn__icontains=value)
        )

    def filter_available(self, queryset, name, value):
        try:
            if value:
                return queryset.filter(copies_available__gt=0)
            return queryset
        except Exception as e:
            logger.error(f"Error in filter_available: {str(e)}")
            return queryset

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'search', 'available', 'published_after', 'published_before', 'year_published']

class AvailableBooksView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BookFilter

    def get_queryset(self):
        try:
            queryset = Book.objects.all()
            return queryset.filter(copies_available__gt=0)
        except Exception as e:
            logger.error(f"Error fetching available books: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            try:
                return Book.objects.none()
            except:
                return []
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in AvailableBooksView.list: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'error': 'Internal server error',
                'message': 'Unable to fetch available books. Please check database connection.',
                'details': str(e) if settings.DEBUG else None
            }, status=500)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
  
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        role = 'member'
        try:
            role = user.userprofile.role
        except:
            pass
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role,
            'refresh': serializer.validated_data['refresh'],
            'access': serializer.validated_data['access'],
            'redirect_url': 'http://localhost:8000/available-books/',
        }, status=200)
    
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f'Token blacklisted successfully for user: {request.user.username}')
            return Response({'message': 'Logged out successfully', 'login_url': reverse('login', request=request)}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f'Error during logout: {str(e)}')

            return Response({'error': 'An error occured while logging out'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def profile_view(request):
    return render(request, 'books/profile.html')

def home(request):
    return render(request, 'books/home.html', {})

def checkout_book_view(request, book_id):
    logger.debug(f'User {request.user.username} checked out book with ID: {book_id}')

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Log request data for debugging
        logger.info(f'Password reset request received')
        logger.info(f'Request data type: {type(request.data)}')
        logger.info(f'Request data: {request.data}')
        logger.info(f'Request MIME type: {request.content_type}')
        
        # Extract email directly from request - handle all possible formats
        email_raw = None
        try:
            # Try different ways to get the email
            if hasattr(request.data, 'get'):
                email_raw = request.data.get('email')
            elif isinstance(request.data, dict):
                email_raw = request.data.get('email')
            elif isinstance(request.data, list) and len(request.data) > 0:
                # Handle JSON array format
                email_raw = request.data[0].get('email') if isinstance(request.data[0], dict) else None
            else:
                # Try to get from request body directly
                import json
                try:
                    body_data = json.loads(request.body)
                    email_raw = body_data.get('email')
                except:
                    pass
            
            logger.info(f'Extracted email: {repr(email_raw)}, type: {type(email_raw)}')
            
            # Also try to get raw request body for debugging
            try:
                import json
                raw_body = request.body.decode('utf-8') if request.body else ''
                logger.info(f'Raw request body: {repr(raw_body)}')
                if raw_body:
                    try:
                        body_json = json.loads(raw_body)
                        logger.info(f'Parsed JSON body: {body_json}')
                    except:
                        logger.info('Request body is not valid JSON')
            except Exception as body_err:
                logger.warning(f'Could not read request body: {str(body_err)}')
        except Exception as e:
            logger.error(f'Error extracting email from request: {str(e)}')
            logger.error(f'Request data type: {type(request.data)}')
            logger.error(f'Request data: {request.data}')
            import traceback
            logger.error(f'Traceback: {traceback.format_exc()}')
            return Response({
                'error': 'Invalid request format. Please check that you are sending a valid email address.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email
        if email_raw is None:
            logger.error('Email is None')
            return Response({
                'error': 'Email address is required.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Convert to string
        try:
            email = str(email_raw).strip()
        except Exception as e:
            logger.error(f'Error converting email to string: {str(e)}')
            return Response({
                'error': 'Invalid email address.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Basic validation
        if not email:
            logger.error('Email is empty')
            return Response({
                'error': 'Email address is required.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # More lenient validation - just check for @ and basic structure
        # Allow emails with + signs, dots, and other valid characters
        if '@' not in email:
            logger.warning(f'Email missing @: {repr(email)}')
            return Response({
                'error': 'Please enter a valid email address.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check that @ is not at the start or end
        if email.startswith('@') or email.endswith('@'):
            logger.warning(f'Email has @ at invalid position: {repr(email)}')
            return Response({
                'error': 'Please enter a valid email address.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Split by @ and check both parts exist
        parts = email.split('@')
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            logger.warning(f'Email has invalid format: {repr(email)}')
            return Response({
                'error': 'Please enter a valid email address.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize email (lowercase) but preserve the original for logging
        email_normalized = email.lower().strip()
        logger.info(f'Processing password reset for: {repr(email_normalized)} (original: {repr(email)})')
        logger.info(f'Email parts - local: {parts[0]}, domain: {parts[1]}')
        
        # Call serializer's save method directly with validated email
        # Create a minimal serializer instance and manually set validated_data
        serializer = self.get_serializer()
        serializer._validated_data = {'email': email_normalized}
        
        # Try to save (send email)
        try:
            logger.info('Attempting to send password reset email...')
            result = serializer.save()
            logger.info(f'Serializer save returned: {result}')
            
            # Check if result indicates email doesn't exist
            if isinstance(result, dict) and result.get('email_exists') == False:
                # Email doesn't exist - return helpful message with signup suggestion
                logger.info('Email does not exist in database')
                return Response({
                    'message': 'No account found with this email address.',
                    'email_exists': False,
                    'suggest_signup': True,
                    'success': True  # Still return success to prevent email enumeration
                }, status=status.HTTP_200_OK)
            
            # Email exists and reset link was sent
            email_backend = getattr(settings, 'EMAIL_BACKEND', '')
            message = 'Password reset link has been sent to your email address.'
            
            # Check if using console backend
            if 'console' in email_backend.lower():
                if settings.DEBUG:
                    # Development: console backend is OK
                    message += ' Please check your Django server console/terminal for the email content.'
                else:
                    # Production: console backend is a problem
                    logger.error('PRODUCTION ERROR: Using console email backend! Emails are not being sent.')
                    return Response({
                        'error': 'Email configuration error: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set in production to send emails.',
                        'success': False
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info('Password reset email sent successfully')
            return Response({
                'message': message,
                'email_exists': True,
                'success': True
            }, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            # This is raised from the serializer with detailed error
            logger.error(f'Password reset validation error: {str(e)}')
            logger.error(f'ValidationError type: {type(e)}')
            logger.error(f'ValidationError has detail: {hasattr(e, "detail")}')
            
            # Extract error message from ValidationError
            error_message = 'Error sending password reset email. Please try again.'
            
            try:
                if hasattr(e, 'detail'):
                    if isinstance(e.detail, dict):
                        # Check for 'email' key first (from serializer)
                        if 'email' in e.detail:
                            email_errors = e.detail['email']
                            if isinstance(email_errors, list) and email_errors:
                                error_message = email_errors[0]
                            elif isinstance(email_errors, str):
                                error_message = email_errors
                        else:
                            # Get first error message from dict
                            first_key = list(e.detail.keys())[0]
                            first_value = e.detail[first_key]
                            if isinstance(first_value, list):
                                error_message = first_value[0] if first_value else str(e.detail)
                            else:
                                error_message = str(first_value)
                    elif isinstance(e.detail, list):
                        error_message = e.detail[0] if e.detail else str(e)
                    else:
                        error_message = str(e.detail)
                else:
                    # If no detail attribute, use string representation
                    error_message = str(e)
                    # Clean up ErrorDetail format if present
                    if 'ErrorDetail' in error_message:
                        import re
                        error_message = re.sub(r"ErrorDetail\(string='([^']+)'.*\)", r'\1', error_message)
                        error_message = error_message.strip("[]'\"")
            except Exception as extract_error:
                logger.error(f'Error extracting ValidationError message: {str(extract_error)}')
                error_message = str(e) if str(e) else 'Error sending password reset email. Please try again.'
                # Clean up error message
                if 'ErrorDetail' in error_message:
                    import re
                    error_message = re.sub(r"ErrorDetail\(string='([^']+)'.*\)", r'\1', error_message)
                    error_message = error_message.strip("[]'\"")
            
            logger.error(f'Returning error to client: {error_message}')
            return Response({
                'error': error_message,
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error with full traceback
            import traceback
            logger.error(f'Password reset error: {str(e)}')
            logger.error(f'Traceback: {traceback.format_exc()}')
            # In development, return more details
            if settings.DEBUG:
                return Response({
                    'error': f'Error sending password reset email: {str(e)}. Check server logs for details.',
                    'success': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'error': 'Error sending password reset email. Please try again later.',
                    'success': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f'Password reset successful for user: {user.username}')
                return Response({
                    'message': 'Password has been reset successfully. You can now login with your new password.',
                    'success': True
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f'Password reset confirm error: {str(e)}')
                return Response({
                    'error': 'Error resetting password. Please try again.',
                    'success': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)