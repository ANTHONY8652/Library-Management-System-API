from rest_framework import filters, permissions, generics, serializers
import django_filters
from django_filters import rest_framework as filters
from .models import Book, Transaction, UserProfile
from .serializers import BookSerializer, TransactionSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.db.models import Q
from .permissions import IsAdminUser, IsMemberUser
from django.shortcuts import render #redirect
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta


##Book CRUD operations
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminUser]

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

##User views
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
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
        transaction = serializer.instance
        if transaction.user == self.request.user.userprofile:
            if transaction.return_date is None:
                transaction.return_date = timezone.now()
                transaction.book.copies_available += 1
                transaction.book.save()
                serializer.save()
            else:
                return serializers.ValidationError('Book already returned')
        else:
            raise serializers.ValidationError('Book already returned.')


class OverdueBooksView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        return Transaction.objects.filter(return_date__isnull=True, due_date__lt=timezone.now())

class BookFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title',lookup_expr='icontains')
    author = filters.CharFilter(field_name='author',lookup_expr='icontains')
    isbn = filters.CharFilter(field_name='isbn',lookup_expr='icontains')
    available = filters.BooleanFilter(field_name='copies_available', lookup_expr='gt', method='filter_available')

    def filter_available(self, queryset, name, value):
        return queryset.filter(copies_available__gt=0)

    class Meta:
        model = Book
        fields = ['title', 'author','isbn', 'available']

class AvailableBooksView(generics.ListAPIView):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BookFilter

    def get_queryset(self):
        queryset = Book.objects.all()
        title = self.request.query_params.get('title', None)
        author = self.request.query_params.get('author', None)
        isbn = self.request.query_params.get('isbn', None)
        available = self.request.query_params.get('available', None)

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)
        if isbn:
            queryset = queryset.filter(isbn__icontains=isbn)
        if available:
            queryset = queryset.filter(copies_available__gt=0)
        
        return queryset

def profile_view(request):
    return render(request, 'books/profile.html')

def home(request):
    return render(request, 'books/home.html', {})

##view to handle search requests
def search_view(request):
    query = request.GET.get('q')
    if query:
        results = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        ).distinct()
    else:
        results = Book.objects.none()
        return render(request, 'books/search_results.html', {'results': results, 'query': query})




"""

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'books'

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = Bookform
    template_name = 'books/book_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().from_valid(form)

class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.author

class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    template_name = 'books/book_form.html'

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.author

##Registration view
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
"""



# Create your views here.