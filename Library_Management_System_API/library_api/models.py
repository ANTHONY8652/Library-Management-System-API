from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    copies_available = models.PositiveIntegerField(default=0)

    def borrow(self):
        if self.is_available():
            self.copies_available -= 1
            self.save()
        else:
            raise Exception('Book is not available for borrowing')
    
    def is_available(self):
        return self.copies_available > 0
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    ADMIN = 'admin'
    MEMBER = 'member'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MEMBER, 'Member'),
    ]
    def validate_role(self):
        if self.role not in ['admin', 'member']:
            raise ValidationError("Role must be either 'admin' or 'member'.")
        
    def validate_loan_duration(self):
        if self.loan_duration <= 0:
            raise ValidationError('Loan duration must be a positive integer')
    
    def clean(self):
        if self.role not in ['admin', 'member']:
            raise ValidationError("Role must be either 'admin' or 'member'")
        if self.loan_duration <= 0:
            raise ValidationError('Loan duration must be a positive integer')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_membership = models.DateField(auto_now_add=True)
    active_status = models.BooleanField(default=True)
    role = models.CharField(max_length=6, choices=ROLE_CHOICES, default='member', validators=[validate_role])
    loan_duration = models.PositiveIntegerField(default=14)
    loan_duration = models.PositiveIntegerField(default=14, validators=[validate_loan_duration])
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.date_of_membership = timezone.now()
        instance.userprofile.save()

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkout_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    overdue_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.checkout_date + timedelta(days=30 if self.user.userprofile.role == 'admin' else 14)
            self.calculate_penalty()
        super().save(*args, **kwargs)

    def mark_as_returned(self):
        self.return_date = timezone.now().date()
        self.book.copies_available += 1
        self.book.save()
        self.save()

    @property
    def is_overdue(self):
        return self.return_date is None and self.due_date < timezone.now().date()
    
    @property
    def is_pending(self):
        return self.return_date is None

    
    def calculate_penalty(self, date=None):
        if date is None:
            date = timezone.now().date()
        if self.is_overdue:
            days_overdue = (date - self.due_date).days
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