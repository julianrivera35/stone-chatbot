from django.contrib import admin
from .models import Brand, Category, Product, UserPreference, ChatSession, ChatMessage, Customer

admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(UserPreference)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
admin.site.register(Customer)
