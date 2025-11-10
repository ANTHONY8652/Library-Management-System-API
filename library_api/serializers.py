from rest_framework import serializers
from .models import Book, UserProfile, Transaction
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
    # For writing: accept book ID (PrimaryKeyRelatedField)
    # For reading: include full book details via to_representation
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), required=False)
    
    def to_representation(self, instance):
        """Include full book details when reading"""
        representation = super().to_representation(instance)
        if instance.book:
            representation['book'] = BookSerializer(instance.book).data
        return representation

    def is_available(self):
        if self.copies_available >= 1:
            return self.book
        else:
            return serializers.ValidationError(f'{self.title} is not available')
    """     
    def validate_book(self, book):
        if book.copies_available <= 0:
            raise serializers.ValidationError('No copies available for checkout')
        return book
    """
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

        # For partial updates (PATCH), we might not have all fields
        # Only validate book if:
        # 1. This is a new transaction (no instance) - book is required for checkout
        # 2. Book is explicitly being updated (in attrs)
        # For return operations, we only update return_date, so book validation is skipped
        if not self.instance:  # New transaction (checkout)
            if not book:
                raise serializers.ValidationError('Book is required')
            # Only check availability for new checkouts
            if book.copies_available == 0:
                raise serializers.ValidationError('No copies available for checkout')
        elif book:  # Existing transaction, but book is being updated
            # If book is being changed, validate availability
            if book.copies_available == 0:
                raise serializers.ValidationError('No copies available for checkout')
        
        return attrs
    
    class Meta:
        model = Transaction
        fields = ['id', 'book', 'user', 'checkout_date', 'return_date', 'due_date', 'overdue_penalty']
        extra_kwargs = {
            'user': {'required': False},  # Set automatically in perform_create
            'checkout_date': {'required': False},  # Can be set in perform_create if not provided
            'due_date': {'required': False},  # Auto-calculated
            'return_date': {'required': False}  # None for new checkouts
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