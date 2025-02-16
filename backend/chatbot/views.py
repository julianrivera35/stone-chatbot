from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import handle_chat_message, clean_expired_sessions
from database.chatbot_models import ChatSession

@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id")
            input_text = data.get("input_text")

            if not input_text:
                return JsonResponse({"error": "No input text provided"}, status=400)

            clean_expired_sessions()

            session = ChatSession.objects.filter(id=session_id).first() if session_id else None

            if not session:
                session = ChatSession.objects.create(user=None)
            session_id, response_text = handle_chat_message(session.user, input_text)

            return JsonResponse({"session_id": session_id, "response_text": response_text})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
