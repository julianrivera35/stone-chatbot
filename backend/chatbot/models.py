import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    M2M100ForConditionalGeneration,
    M2M100Tokenizer,
    pipeline
)


class AIModelManager:
    _instance = None
    INTENT_MODEL_PATH = "./intent_model" 
    INTENT_LABELS = [
        "consulta_precio",
        "consulta_inventario", 
        "caracteristicas_producto",
        "consulta_recomendaciones",
        "saludo",
        "despedida"
    ]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIModelManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._dialog = None
        self._translation = None
        self._intent_classifier = None
        self._ner_pipeline = None
        
    @property
    def dialog(self):
        if not self._dialog:
            self._load_dialog_model()
        return self._dialog
    
    @property
    def translation(self):
        if not self._translation:
            self._load_translation_model()
        return self._translation
    
    @property
    def intent_classifier(self):
        if not self._intent_classifier:
            self._load_intent_model()
        return self._intent_classifier
    
    @property
    def ner_pipeline(self):
        if not self._ner_pipeline:
            self._load_ner_model()
        return self._ner_pipeline
    

    def _load_dialog_model(self):
        try:
            tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            tokenizer.pad_token = tokenizer.eos_token
            model = AutoModelForCausalLM.from_pretrained(
                "microsoft/DialoGPT-medium"
            ).to(self.device)
            self._dialog = (tokenizer, model)
        except Exception as e:
            raise RuntimeError(f"Error loading dialog model: {str(e)}")
    
    def _load_translation_model(self):
        try:
            tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
            model = M2M100ForConditionalGeneration.from_pretrained(
                "facebook/m2m100_418M"
            ).to(self.device)
            self._translation = (tokenizer, model)
        except Exception as e:
            raise RuntimeError(f"Error loading translation model: {str(e)}")
    
    def _load_intent_model(self):
        try:
            self._intent_classifier = pipeline(
                "text-classification",
                model="./intent_model",
                tokenizer="./intent_model",
                device=self.device,
                framework="pt"
            )
        except Exception as e:
            raise RuntimeError(f"Error loading intent classifier: {str(e)}")
    
    def _load_ner_model(self):
        try:
            self._ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english",
                device=self.device,
                grouped_entities=True
            )
        except Exception as e:
            raise RuntimeError(f"Error loading NER model: {str(e)}")

    def detect_intent(self, text: str, threshold: float = 0.2) -> str:
        result = self.intent_classifier(text)[0]
        return result['label'] if result['score'] >= threshold else "desconocido"
    
    def translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        tokenizer, model = self.translation
        tokenizer.src_lang = src_lang
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        output_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.get_lang_id(tgt_lang))
        return tokenizer.batch_decode(output_tokens, skip_special_tokens=True)[0]
    
    def generate_response(self, input_text: str) -> str:
        dialog_tokenizer, dialog_model = self.dialog
        input_en = self.translate_text(input_text, "es", "en")
        
        inputs = dialog_tokenizer(
            input_en + dialog_tokenizer.eos_token,
            return_tensors="pt"
        ).to(dialog_model.device)
        
        outputs = dialog_model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=128,
            pad_token_id=dialog_tokenizer.eos_token_id,
            temperature=0.7,
            top_k=50
        )
        
        response_en = dialog_tokenizer.decode(
            outputs[0][inputs.input_ids.shape[-1]:],
            skip_special_tokens=True
        )
        return self.translate_text(response_en, "en", "es")
    
    def extract_product_entities(self, text: str) -> list:
        entities = self.ner_pipeline(text)
        return [
            {
                'entity': entity['entity_group'],
                'word': entity['word'].replace('▁', ' ').strip(),
                'score': round(entity['score'], 3)
            }
            for entity in entities
            if entity['entity_group'] == 'PRODUCT'
        ]

ai_model_manager = AIModelManager()