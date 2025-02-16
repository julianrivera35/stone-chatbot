import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, M2M100ForConditionalGeneration, M2M100Tokenizer
from django.utils.timezone import now, timedelta
from database.chatbot_models import ChatSession, ChatMessage
from database.user_models import Customer

def load_models():
    dialog_model_name = "microsoft/DialoGPT-medium"
    translation_model_name = "facebook/m2m100_418M"

    dialog_tokenizer = AutoTokenizer.from_pretrained(dialog_model_name)
    if dialog_tokenizer.pad_token is None:
        dialog_tokenizer.pad_token = dialog_tokenizer.eos_token
        dialog_tokenizer.pad_token_id = dialog_tokenizer.eos_token_id
    dialog_model = AutoModelForCausalLM.from_pretrained(dialog_model_name)

    translation_tokenizer = M2M100Tokenizer.from_pretrained(translation_model_name)
    translation_model = M2M100ForConditionalGeneration.from_pretrained(translation_model_name)

    return dialog_tokenizer, dialog_model, translation_tokenizer, translation_model

dialog_tokenizer, dialog_model, translation_tokenizer, translation_model = load_models()

def translate_text(text, src_lang, tgt_lang):
    translation_tokenizer.src_lang = src_lang
    inputs = translation_tokenizer(text, return_tensors="pt")
    output_tokens = translation_model.generate(**inputs, forced_bos_token_id=translation_tokenizer.get_lang_id(tgt_lang))
    return translation_tokenizer.batch_decode(output_tokens, skip_special_tokens=True)[0]

def get_chatbot_response(input_text, chat_history=None):
    input_text_en = translate_text(input_text, "es", "en")
    input_ids = dialog_tokenizer.encode(input_text_en + dialog_tokenizer.eos_token, return_tensors="pt")
    attention_mask = input_ids.ne(dialog_tokenizer.pad_token_id).long()
    response_ids = dialog_model.generate(input_ids, attention_mask=attention_mask, max_length=100, pad_token_id=dialog_tokenizer.eos_token_id)
    response_text_en = dialog_tokenizer.decode(response_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
    response_text_es = translate_text(response_text_en, "en", "es")
    return response_text_es

def get_or_create_chat_session(user=None):
    if user:
        session = ChatSession.objects.filter(user=user).first()
        if not session:
            session = ChatSession(user=user)
            session.save()
    else:
        session = ChatSession.objects.create(user=None)
    return session

def handle_chat_message(user, text):
    session = get_or_create_chat_session(user)
    ChatMessage.objects.create(session=session, sender="user", text=text)
    if text.strip().lower() == "salir":
        farewell_message = "¡Hasta luego! Si necesitas algo más, no dudes en escribirme."
        ChatMessage.objects.create(session=session, sender="chatbot", text=farewell_message)
        session.delete()
        return None, farewell_message
    bot_response = get_chatbot_response(text)
    ChatMessage.objects.create(session=session, sender="chatbot", text=bot_response)
    session.last_active = now()
    session.save()
    return session.id, bot_response

def clean_expired_sessions():
    # Function to clean expired chat sessions
    for session in ChatSession.objects.all():
        if session.is_expired():
            session.delete()
