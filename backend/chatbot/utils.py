import re
from database.product_models import Brand, Category, Product
from fuzzywuzzy import process
import unidecode

def get_known_brands():
    return list(Brand.objects.values_list("name", flat=True))

def get_known_categories():
    return list(Category.objects.values_list("name", flat = True))

def get_known_products():
    products = Product.objects.values_list("id", "name")
    product_dict = {}
    for id, name in products:
        product_dict[normalize_text(name)] = id
        product_dict[name] = id
    return product_dict

def normalize_text(text):
    return unidecode.unidecode(text.lower().strip())

def extract_query_info(input_text, intent):
    category = None
    brand = None
    input_text = input_text.lower()
    words = input_text.split()

    brands = get_known_brands()
    categories = get_known_categories()
    products_dict = get_known_products()
    print(products_dict.items())

    KNOWN_BRANDS = [b.lower() for b in brands]
    KNOWN_CATEGORIES = [c.lower() for c in categories]
    
    if intent in ["consulta_precio", "consulta_inventario", "caracteristicas_producto"]:
        match = re.search(r"(?:cuanto cuesta|cuánto cuesta|stock de|características de):?\s*(.+)", input_text, re.IGNORECASE)

        product_name = match.group(1).strip() if match else input_text.strip()
        normalized_name = normalize_text(product_name)
        
        print(f"Debug - Normalized name: {normalized_name}") 
        print(f"Debug - Available products: {list(products_dict.keys())}") 
        
        if normalized_name in products_dict:
            return [products_dict[normalized_name]]
        else:
            # If no exact match, try fuzzy matching
            best_match, score = process.extractOne(normalized_name, products_dict.keys())
            print(f"Debug - Best match: {best_match}, Score: {score}") 
            if score > 80:
                return [products_dict[best_match]]
        return None

    elif intent == "consulta_categoria":
        category = next((c for c in KNOWN_CATEGORIES if c in words), None)
        return category if category else None

    elif intent == "consulta_marca":
        brand = next((b for b in KNOWN_BRANDS if b in words), None)
        return brand if brand else None

    elif intent == "consulta_mixta":
        category = next((c for c in KNOWN_CATEGORIES if c in words), None)
        brand = next((b for b in KNOWN_BRANDS if b in words), None)
        
        if category and brand:
            return category, brand
        return None

    if intent == "consulta_multiproducto":
        match = re.search(r"(?:tienen los productos|quiero ver|busco|cuanto cuestan):?\s*(.+)", input_text, re.IGNORECASE)
        if match:
            product_part = match.group(1)
            product_names = re.split(r'\s+y\s+|,\s*', product_part)
        else:
            product_names = [input_text]
            
        products_dict = get_known_products()
        found_product_ids = []
        
        print(f"Debug - Product names to search: {product_names}")
        
        for name in product_names:
            name = name.strip()
            normalized_name = normalize_text(name)
            print(f"Debug - Processing name: {name}")
            print(f"Debug - Normalized name: {normalized_name}")
            
            if name in products_dict:
                found_product_ids.append(products_dict[name])
            elif normalized_name in products_dict:
                found_product_ids.append(products_dict[normalized_name])
            else:
                available_names = list(products_dict.keys())
                best_match, score = process.extractOne(normalized_name, available_names)
                print(f"Debug - Best fuzzy match: {best_match}, Score: {score}")
                
                if score > 80:
                    found_product_ids.append(products_dict[best_match])
        
        print(f"Debug - Final product IDs found: {found_product_ids}")
        return found_product_ids if found_product_ids else None

    return None