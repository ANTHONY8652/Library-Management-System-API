from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import  (
    home, profile_view, OverdueBooksView, BookListCreateView, BookDetailView, UserProfileDetailView, UserProfileListCreateView, ReturnBookview, AvailableBooksView, CheckOutBookView, UserRegistrationView, UserLoginView, UserLogoutView, MyTokenObtainPairView
 )
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    ##register view
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    ##LOgin and logout views
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    ##Token Views
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', MyTokenObtainPairView.as_view, name='token-verify'),
    #profile_view
    path('profile/', profile_view, name='profile'),
    ##Home View
    path('home/', home, name='home'),
    ##Boooks urls
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    ##Users urls
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password-reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view, name='password-reset-done'),
    path('users/', UserProfileListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserProfileDetailView.as_view(), name='user-detail'),
    ##Books transaction urls
    path('checkout/', CheckOutBookView.as_view(), name='checkout-book'),
    path('return/<int:pk>/', ReturnBookview.as_view(), name='return-book'),
    path('available-books/', AvailableBooksView.as_view(), name='available-books'),
    path('overdue-books/', OverdueBooksView.as_view(), name='overdue-books'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)