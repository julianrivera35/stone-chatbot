from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomerUseManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Customer(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    role= models.CharField(
        max_length=20,
        choices=[("customer", "Customer"), ("admin", "Admin"), ("seller", "Seller")],
    )
    created_at= models.DateTimeField(auto_now_add=True)
    date_of_birth= models.DateField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomerUseManager()

    def __str__(self):
        return self.email