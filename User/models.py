from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User,primary_key=True, on_delete=models.CASCADE)
    phone=models.CharField(max_length=11)
    address=models.CharField(max_length=100)
    ratings_sum = models.IntegerField(default=0)
    ratings_count = models.IntegerField(default=0)
    birth_date = models.DateField(null=True, blank=True)
    amount = models.IntegerField(default=0,null=True, blank=True)

    def __str__(self):
        return self.user.username



