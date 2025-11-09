from rest_framework import filters, permissions, generics, serializers, status
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from .models import Book, Transaction, UserProfile
from .serializers import BookSerializer, TransactionSerializer, UserProfileSerializer, UserRegistrationSerializer, UserLoginSerializer, TokenObtainPairSerializer
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

# Pagination classes
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

##Book CRUD operations
class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to view, can restrict create later
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['title', 'published_date']
    
    def get_queryset(self):
        """Override to handle potential database errors"""
        try:
            # Try to get books - let Django handle the connection
            return Book.objects.all().order_by('title', 'author')
        except Exception as e:
            logger.error(f"Error fetching books: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # Return empty queryset to avoid crashing
            try:
                return Book.objects.none()
            except:
                # If even .none() fails, return empty list
                return []
    
    def list(self, request, *args, **kwargs):
        """Override list to handle errors gracefully"""
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
    permission_classes = [CanViewBook]  # Simplified - CanViewBook handles both read and write
    
    def get_queryset(self):
        """Get queryset with error handling"""
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

##User views
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Get user role from profile
            role = 'member'  # default
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


##Transaction ViewSsss Controller

class CheckOutBookView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]

    def perform_create(self, serializer):
        book = serializer.validated_data.get('book')
        if not book:
            raise serializers.ValidationError('Book is required')
        
        if book.copies_available > 0:
            # Check for outstanding transactions
            try:
                if self.request.user.userprofile.has_outstanding_transactions(book):
                    raise serializers.ValidationError('You already have an outstanding transaction for this book')
            except Exception as e:
                # If userprofile doesn't exist or other error, log and continue
                logger.error(f'Error checking outstanding transactions: {e}')
            
            # Decrease available copies
            book.copies_available -= 1
            book.save()
            
            # Calculate due date based on user role (14 days for members, 30 for admins)
            try:
                user_profile = self.request.user.userprofile
                loan_days = 30 if user_profile.role == 'admin' else 14
            except:
                # Default to 14 days if userprofile doesn't exist
                loan_days = 14
                logger.warning(f'UserProfile not found for user {self.request.user.username}, using default loan duration')
            
            due_date = timezone.now().date() + timedelta(days=loan_days)
            
            # Get checkout_date from validated_data or use today
            checkout_date = serializer.validated_data.get('checkout_date') or timezone.now().date()
            
            # Save transaction with User (not UserProfile) and auto-calculated due_date
            serializer.save(
                user=self.request.user,  # Transaction.user is ForeignKey to User, not UserProfile
                checkout_date=checkout_date,
                due_date=due_date,
                return_date=None  # Explicitly set to None for new checkout
            )
        else:
            raise serializers.ValidationError('No copies available for checkout')

class ReturnBookview(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]

    def perform_update(self, serializer):
        try:
            transaction = serializer.instance
            # Check if user owns this transaction and it's not already returned
            if transaction.user == self.request.user and transaction.return_date is None:
                # Set return date to today
                transaction.return_date = timezone.now().date()  # Use .date() not datetime
                
                # Increase available copies
                transaction.book.copies_available += 1
                transaction.book.save()
                
                # Recalculate penalty if overdue
                transaction.calculate_penalty()
                
                # Save the transaction
                serializer.save()
            else:
                if transaction.return_date is not None:
                    raise serializers.ValidationError('This book has already been returned.')
                else:
                    raise serializers.ValidationError('You are not authorized to return this book.')
        except serializers.ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MyBooksView(generics.ListAPIView):
    """Get all currently borrowed books (not returned) for the authenticated user"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Transaction.objects.filter(
            return_date__isnull=True,
            user=self.request.user
        ).select_related('book').order_by('-checkout_date')

class TransactionHistoryView(generics.ListAPIView):
    """Get all transactions (including returned) for the authenticated user"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).select_related('book').order_by('-checkout_date')

class CurrentUserProfileView(generics.RetrieveAPIView):
    """Get current user's profile"""
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
    available = filters.BooleanFilter(field_name='copies_available', lookup_expr='gt', method='filter_available')
    published_after = filters.DateFilter(field_name='published_date', lookup_expr='gte')
    published_before = filters.DateFilter(field_name='published_date', lookup_expr='lte')
    year_published = filters.NumberFilter(field_name='published_date', lookup_expr='year')

    def filter_available(self, queryset, name, value):
        """Filter books by availability"""
        try:
            if value:
                return queryset.filter(copies_available__gt=0)
            return queryset
        except Exception as e:
            logger.error(f"Error in filter_available: {str(e)}")
            return queryset

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'available', 'published_after', 'published_before', 'year_published']

class AvailableBooksView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to view available books
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BookFilter

    def get_queryset(self):
        """Get available books with error handling"""
        try:
            # Try to get available books
            queryset = Book.objects.all()
            return queryset.filter(copies_available__gt=0)
        except Exception as e:
            logger.error(f"Error fetching available books: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            # Return empty queryset to avoid crashing
            try:
                return Book.objects.none()
            except:
                # If even .none() fails, return empty list
                return []
    
    def list(self, request, *args, **kwargs):
        """Override list to handle errors gracefully"""
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
        
        # Get user role from profile
        role = 'member'  # default
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

#check if your token is still valid view
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

# Create your views here.