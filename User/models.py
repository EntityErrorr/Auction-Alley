from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=100)
    ratings_sum = models.IntegerField(default=0)
    ratings_count = models.IntegerField(default=0)
    birth_date = models.DateField(null=True, blank=True)
    amount = models.IntegerField(default=0, null=True, blank=True)
    
    # Membership fields
    membership_start_date = models.DateTimeField(null=True, blank=True)
    membership_end_date = models.DateTimeField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    
    # Profile picture field (only for premium members)
    profile_picture = models.ImageField(upload_to='images/profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.username

    def activate_membership(self):
        self.membership_start_date = timezone.now()
        self.membership_end_date = self.membership_start_date + timedelta(days=180)  # 6 months
        self.is_premium = True
        self.save()

    def is_membership_active(self):
        if self.membership_end_date and self.membership_end_date >= timezone.now():
            return True
        return False

    def save(self, *args, **kwargs):
        # Ensure that only premium members can have a profile picture
        if not self.is_premium:
            self.profile_picture = None
        super().save(*args, **kwargs)
