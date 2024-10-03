from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateTimeField()
    copies_available = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    ADMIN = 'admin'
    MEMBER = 'member'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_membership = models.DateField(auto_now_add=True)
    active_status = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.CharField(max_length=6, choices=ROLE_CHOICES, default='MEMBER')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

    def __str__(self):
        return self.user.username

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        #Set due date to 14 days after checkout
        if not self.due_date:
            self.due_date = self.checkout_date + timedelta(days=14)
            super().save(*args, **kwargs)
    @property
    def is_overdue(self):
        return self.retun_date is None and self.due_date  < timezone.now().date()
    
    def __str__(self):
        return f"{self.user.username} checked out {self.book.title} remaining copies available {self.book.copies_available} copies"


# Create your models here.
