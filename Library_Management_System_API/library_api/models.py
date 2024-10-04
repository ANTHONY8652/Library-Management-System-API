from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    copies_available = models.PositiveIntegerField(default=0)

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
    role = models.CharField(max_length=6, choices=ROLE_CHOICES, default='member')
    loan_duration = models.PositiveIntegerField(default=14)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkout_date = models.DateField()
    return_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    overdue_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.checkout_date + timedelta(days=30 if self.user.userprofile.role == 'admin' else 14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.return_date is None and self.due_date < timezone.now().date()
    
    def calculate_penalty(self):
        if self.is_overdue:
            days_overdue =(timezone.now().date() - self.due_date).days
            if self.user.userprofile.role == 'admin':
                penalty_per_day = 0.50
            else:
                penalty_per_day = 1.00
            if days_overdue <= 7:
                penalty_per_day = 1.00
            else:
                penalty_per_day = 2.00
            
            self.overdue_penalty = days_overdue * penalty_per_day

    def __str__(self):
        return f"{self.user.username} checked out {self.book.title}"