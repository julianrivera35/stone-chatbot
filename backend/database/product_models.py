from django.db import models
from .user_models import Customer

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    specifications = models.JSONField()
    stock = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.brand} {self.name}"
    
class UserPreference(models.Model):
    user = models.OneToOneField(Customer,on_delete=models.CASCADE, related_name="preferences")
    preferred_brands = models.ManyToManyField(Brand, blank=True)
    preferred_categories = models.ManyToManyField(Category, blank=True)
    budget_range = models.JSONField(default=dict)
    purchase_history = models.JSONField(default=list)
    
    def __str__(self):
        return f"Preferencias de {self.user.email}"