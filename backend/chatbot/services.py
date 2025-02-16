from django.utils.timezone import now, timedelta
from database.chatbot_models import ChatSession, ChatMessage
from database.user_models import Customer
from database.product_models import Product, UserPreference
from .models import ai_model_manager
from rapidfuzz.fuzz import ratio
from fuzzywuzzy import process
import re



def handle_chat_message(user, text):
    session = get_or_create_chat_session(user)
    ChatMessage.objects.create(session=session, sender="user", text=text)

    intent = ai_model_manager.detect_intent(text)
    intent = intent.strip().strip('"')

    response = 'Hola'
    
    if intent == "desconocido":
        response = "No estoy seguro de entender. ¿Podrías reformular tu pregunta?"
    if intent == "saludo":
        response = "¡Hola! Soy tu asistente de Buy n Large. ¿En qué puedo ayudarte?"
    if intent == "despedida":
        response = "¡Gracias por contactarnos! No dudes en escribirme si necesitas más ayuda."
        ChatMessage.objects.create(session=session, sender="chatbot", text=response)
        session.delete()
        return None, response
    if intent in ["consulta_precio", "consulta_inventario", "caracteristicas_producto"]:
        if ":" not in text:
            return session.id, "Por favor, escribe tu consulta de esta forma: '¿Cuánto cuesta: [nombre del producto]?' o '¿Cuál es el stock de: [nombre del producto]?'"
        product_part = text.split(":", 1)[1].strip()  
        product_entities = ai_model_manager.extract_product_entities(product_part)
        product_names = [entity['word'] for entity in product_entities] if product_entities else []
        
        if product_names:
            main_product = product_names[0]
        else:
            raw_product_name = text.split(":")[-1].strip()
            clean_name = clean_product_name(raw_product_name)
            main_product = find_best_match(clean_name)

        if main_product is None:
            return session.id, f"No encontramos '{product_part}' en el inventario. ¿Puedes verificar el nombre?"
        response = handle_product_query(intent, main_product)

    if intent == "consulta_recomendaciones":
        response = handle_recommendations(user)
    
    

    ChatMessage.objects.create(session=session, sender="chatbot", text=response)
    session.last_active = now()
    session.save()
    return session.id, response

def get_all_product_names():
    return list(Product.objects.values_list("name", flat=True))

def clean_product_name(name):
    return re.sub(r"[^\w\s]", "", name).strip().lower()

def find_best_match(product_name):
    productos_db = get_all_product_names()
    best_match, score = process.extractOne(product_name, productos_db) if productos_db else (None, 0)

    if best_match and score >= 95:  
        return best_match  
    return None

def handle_product_query(intent, product_name):
    print(f"[DEBUG] Producto recibido en handle_product_query: {product_name}")
    
    product = Product.objects.filter(name=product_name).first()
    
    if not product:
        print(f"[DEBUG] Producto '{product_name}' no encontrado en la base de datos.")
        return f"Lo siento, pero no encontramos '{product_name}' en nuestro inventario."
    
    if intent == "consulta_precio":
        return f"El precio de {product.name} es ${product.price}"
    
    elif intent == "consulta_inventario":
        return f"{product.name}: Stock: {product.stock} unidades"
    
    elif intent == "caracteristicas_producto":
        return f"Características de {product.name}: {product.specifications}"
    
    return "No pude procesar tu consulta, intenta reformularla."




def handle_recommendations(user):
    if not user:
        return "⚠️ Para recomendaciones personalizadas, por favor inicia sesión."
    
    try:
        prefs = UserPreference.objects.get(user=user)
        products = Product.objects.filter(
            category__in=prefs.preferred_categories.all(),
            brand__in=prefs.preferred_brands.all(),
            price__range=(prefs.budget_range.get('min', 0), prefs.budget_range.get('max', 99999))
        )[:5]  # Limitar a 5 recomendaciones
        
        return "🎁 Recomendaciones personalizadas:\n" + "\n".join(
            f"- {p.name} (${p.price})" for p in products
        ) if products.exists() else "¿Qué tipo de productos te interesan hoy?"
    
    except UserPreference.DoesNotExist:
        return "Cuéntame tus preferencias para darte mejores recomendaciones."

def get_or_create_chat_session(user=None):
    if user:
        session = ChatSession.objects.filter(user=user).first()
        if not session:
            session = ChatSession(user=user)
            session.save()
    else:
        session = ChatSession.objects.create(user=None)
    return session

def clean_expired_sessions():
    for session in ChatSession.objects.all():
        if session.is_expired():
            session.delete()