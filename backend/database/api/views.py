from .permissions import IsAdminOrReadOnly, IsCustomerOwner, IsSellerOrAdmin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from ..models import Product, UserPreference, Brand, Category, Customer, ChatSession, ChatMessage
from .serializers import ProductSerializer, UserPreferenceSerializer, BrandSerializer, CategorySerializer, CustomerSerializer, ChatSessionSerializer, ChatMessageSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsCustomerOwner]

class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsCustomerOwner]

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsCustomerOwner]
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsSellerOrAdmin]
    
@api_view(['POST'])
@permission_classes([AllowAny])
def register_customer(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '').strip()
    role = request.data.get('role', 'customer')

    if not email or not password:
        return Response({"error": "El email y la contraseña son obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

    if Customer.objects.filter(email=email).exists():
        return Response({"error": "El correo electrónico ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Crear el usuario sin 'username'
        customer = Customer.objects.create_user(email=email, password=password, role=role)

        return Response({
            "message": "Usuario registrado con éxito.",
            "customer": CustomerSerializer(customer).data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"Error al registrar usuario: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
