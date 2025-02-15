from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import get_chatbot_response

@csrf_exempt
def chatbot_view(request):
    # Function to receive messages and return responses from the AI
    if request.method == 'POST':
        data = json.loads(request.body)
        input_text = data.get('input_text','')
        
        if not input_text:
            return JsonResponse({'error': 'El mensaje no puede estar vacío.'},status=400)
        
        response = get_chatbot_response(input_text)
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Método no permitido.'}, status=405)