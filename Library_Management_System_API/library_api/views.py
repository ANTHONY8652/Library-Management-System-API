from rest_framework import filters, permissions, generics, serializers, status
from django_filters import rest_framework as filters
from .models import Book, Transaction, UserProfile
from .serializers import BookSerializer, TransactionSerializer, UserProfileSerializer, UserRegistrationSerializer, UserLoginSerializer
from .permissions import IsAdminUser, IsMemberUser, CanDeleteBook, CanViewBook
from django.shortcuts import render
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

##Book CRUD operations
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminUser, CanViewBook]
    ordering_fields = ['title', 'published_date']


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, CanViewBook, CanDeleteBook]

    def perform_destroy(self, instance):
        if instance.copies_available > 0:
            raise serializers.ValidationError('You cannot delete a book that has copies available')
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
            refresh = RefreshToken.for_user(user)

            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=201)
        return Response(serializer.errors, status=400)
        
"""""
        except serializers.ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({'error': 'An error occurred during registration'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
"""""


class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all().order_by('id')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


##Transaction ViewSsss Controller

class CheckOutBookView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsMemberUser]

    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        if book.copies_available > 0:
            if self.request.user.userprofile.has_outstanding_transactions(book):
                raise serializers.ValidationError('You already have an outstanding transaction for this book')
            book.copies_available -= 1
            book.save()
            due_date = timezone.now() + timedelta(days=14)
            serializer.save(user=self.request.user.userprofile, due_date=due_date)
        else:
            raise serializers.ValidationError('No copies available for checkout')

class ReturnBookview(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        try:
            transaction = serializer.instance
            if transaction.user == self.request.user.userprofile and transaction.return_date is None:
                transaction.return_date = timezone.now()
                transaction.book.copies_available += 1
                transaction.book.save()
                serializer.save()
            else:
                raise serializers.ValidationError('You are not authorized to return this book.')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OverdueBooksView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(return_date__isnull=True, due_date__lt=timezone.now(), user=self.request.user.userprofile)

class BookFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title',lookup_expr='icontains')
    author = filters.CharFilter(field_name='author',lookup_expr='icontains')
    isbn = filters.CharFilter(field_name='isbn',lookup_expr='icontains')
    available = filters.BooleanFilter(field_name='copies_available', lookup_expr='gt', method='filter_available')
    published_after = filters.DateFilter(field_name='published_date', lookup_expr='gte')
    published_before = filters.DateFilter(field_name='published_date', lookup_expr='lte')
    year_published = filters.NumberFilter(field_name='published_date', lookup_expr='year')

    def filter_available(self, queryset, name, value):
        return queryset.filter(copies_available__gt=0)

    class Meta:
        model = Book
        fields = ['title', 'author','isbn', 'available', 'published_after', 'published_before', 'year_published']

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'total_items': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

class MyCursorPagination(CursorPagination):
    page_size = 10
    ordering = 'published_date'

class AvailableBooksView(generics.ListAPIView):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BookFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(copies_available__gt=0)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=200)
    
class UserLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully', 'login_url': reverse('login', request=request)}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

def profile_view(request):
    return render(request, 'books/profile.html')

def home(request):
    return render(request, 'books/home.html', {})

def checkout_book_view(request, book_id):
    logger.debug(f'User {request.user.username} checked out book with ID: {book_id}')

# Create your views here.