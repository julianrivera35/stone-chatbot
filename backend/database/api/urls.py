from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BrandViewSet, CategoryViewSet, ProductViewSet, UserPreferenceViewSet,
    ChatSessionViewSet, ChatMessageViewSet, CustomerViewSet
)

router = DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'preferences', UserPreferenceViewSet)
router.register(r'chat-sessions', ChatSessionViewSet)
router.register(r'chat-messages', ChatMessageViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
