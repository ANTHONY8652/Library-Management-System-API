from django.contrib import admin
from .models import Book, UserProfile, Transaction

admin.site.register(Book)
admin.site.register(Transaction)
admin.site.register(UserProfile)

# Register your models here.
