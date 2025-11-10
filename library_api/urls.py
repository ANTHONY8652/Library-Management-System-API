from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import  (
    home, profile_view, OverdueBooksView, MyBooksView, TransactionHistoryView, CurrentUserProfileView, BookListCreateView, BookDetailView, UserProfileDetailView, UserProfileListCreateView, ReturnBookview, AvailableBooksView, CheckOutBookView, UserRegistrationView, UserLoginView, UserLogoutView, MyTokenObtainPairView
 )
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', MyTokenObtainPairView.as_view(), name='token-verify'),
    path('profile/', profile_view, name='profile'),
    path('home/', home, name='home'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password-reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view, name='password-reset-done'),
    path('users/', UserProfileListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserProfileDetailView.as_view(), name='user-detail'),
    path('checkout/', CheckOutBookView.as_view(), name='checkout-book'),
    path('return/<int:pk>/', ReturnBookview.as_view(), name='return-book'),
    path('available-books/', AvailableBooksView.as_view(), name='available-books'),
    path('my-books/', MyBooksView.as_view(), name='my-books'),
    path('transaction-history/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('overdue-books/', OverdueBooksView.as_view(), name='overdue-books'),
    path('my-profile/', CurrentUserProfileView.as_view(), name='current-user-profile'),
]