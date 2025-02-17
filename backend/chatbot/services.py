from django.utils.timezone import now, timedelta
from database.chatbot_models import ChatSession, ChatMessage
from database.user_models import Customer
from database.product_models import Product, UserPreference
from .models import ai_model_manager
from rapidfuzz.fuzz import ratio
from fuzzywuzzy import process
import re
from .utils import extract_query_info
from django.db.models import F



def handle_chat_message(user, text):
    session = get_or_create_chat_session(user)
    ChatMessage.objects.create(session=session, sender="user", text=text)

    intent = ai_model_manager.detect_intent(text)
    intent = intent.strip().strip('"')
    print('INTENT: ', intent)
    response = "No estoy seguro de entender. ¿Podrías reformular tu pregunta?"
    
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
    
    elif intent in ["consulta_categoria", "consulta_marca", "consulta_mixta", "consulta_multiproducto"]:
        response = handle_product_query(intent, text)


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

    if best_match and score >= 75:  
        return best_match  
    return None

def handle_product_query(intent, input_text):
    """Procesa la consulta según la intención detectada y filtra productos en la BD."""
    
    if intent in ["consulta_precio", "consulta_inventario", "caracteristicas_producto"]:
        product_ids = extract_query_info(input_text, intent)
        print(f"Debug - Input text: {input_text}")
        print(f"Debug - Product IDs found: {product_ids}")
        
        if not product_ids or len(product_ids) == 0:
            return {"error": "No se encontró el producto especificado."}
            
        product = Product.objects.filter(id=product_ids[0]).select_related('brand', 'category').first()
        if not product:
            return {"error": "No se encontró el producto especificado."}
            
        if intent == "consulta_precio":
            return {
                "message": f"El precio de {product.name} es ${product.price}",
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "brand_name": product.brand.name,
                    "category_name": product.category.name
                }
            }
        
        elif intent == "consulta_inventario":
            return {
                "message": f"{product.name}: Stock: {product.stock} unidades",
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "stock": product.stock,
                    "brand_name": product.brand.name,
                    "category_name": product.category.name
                }
            }
        
        elif intent == "caracteristicas_producto":
            return {
                "message": f"Características de {product.name}:",
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "specifications": product.specifications,
                    "description": product.description,
                    "brand_name": product.brand.name,
                    "category_name": product.category.name
                }
            }

    elif intent == "consulta_categoria":
        category = extract_query_info(input_text, intent)
        if category:
            products = Product.objects.filter(category__name__iexact=category)
            return {"category": category, "products": list(products.values())}
        return {"error": "No se encontraron productos para esa categoría."}

    elif intent == "consulta_marca":
        brand = extract_query_info(input_text, intent)
        if brand:
            products = Product.objects.filter(brand__name__iexact=brand)
            return {"brand": brand, "products": list(products.values())}
        return {"error": "No se encontraron productos para esa marca."}

    elif intent == "consulta_mixta":
        category, brand = extract_query_info(input_text, intent) or (None, None)

        if category is None and brand is None:
            return {"error": "No se encontraron productos con esos nombres."}

        if brand and not category:
            products = Product.objects.filter(brand__name__iexact=brand)
        elif category and not brand:
            products = Product.objects.filter(category__name__iexact=category)
        else:
            products = Product.objects.filter(brand__name__iexact=brand, category__name__iexact=category)
        
        if not products.exists():
            return {"error": "No se encontraron productos disponibles en esa categoría o marca."}

        return list(products.values("name", "price"))

    elif intent == "consulta_multiproducto":
        product_ids = extract_query_info(input_text, intent)
        print(f"Product IDs received: {product_ids}")
        
        if product_ids:
            products = Product.objects.filter(id__in=product_ids).select_related('brand', 'category')
            return {
                "products": list(products.values(
                    "id", 
                    "name", 
                    "price",
                    "description",
                    brand_name=F('brand__name'),
                    category_name=F('category__name')
                ))
            }
        return {"error": "No se encontraron productos con esos nombres."}

    return {"error": "No se pudo procesar la consulta."}


def handle_recommendations(user):
    if not user:
        return "Para recomendaciones personalizadas, por favor inicia sesión."
    
    try:
        prefs = UserPreference.objects.get(user=user)
        products = Product.objects.filter(
            category__in=prefs.preferred_categories.all(),
            brand__in=prefs.preferred_brands.all(),
            price__range=(prefs.budget_range.get('min', 0), prefs.budget_range.get('max', 99999))
        )[:5]
        
        return "Recomendaciones personalizadas:\n" + "\n".join(
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