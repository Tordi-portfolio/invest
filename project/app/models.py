from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=20.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet"


class Plan(models.Model):
    name = models.CharField(max_length=100)
    plan = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=10, default=0.00)
    roi = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    time = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"