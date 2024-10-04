from rest_framework import serializers
from .models import Book, UserProfile, Transaction
from django.contrib.auth.models import User

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'book', 'user', 'checkout_date', 'return_date', 'due_date']

    def validate(self, attrs):
        book = attrs.get('book')

        if book.copies_available <= 0:
            raise serializers.ValidationError('No copies available for checkout.')
        
        return attrs

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    email = serializers.CharField(required=True, unique=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('Password must contain at least one number.')
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError('Password must contain at least one letter.')


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user