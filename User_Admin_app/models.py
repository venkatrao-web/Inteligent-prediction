from django.db import models

class CustomUser(models.Model):
    full_name = models.CharField(max_length=100, default='', blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    mobile = models.CharField(max_length=15, default='', blank=True)
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128, default='')
    agree = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # ✅ New field for admin approval

    def __str__(self):
        return self.username
