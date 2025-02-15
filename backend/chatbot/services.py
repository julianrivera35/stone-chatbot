from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the model
tokenizer = AutoTokenizer.from_pretrained("bert-base-spanish-wwm-cased")
model = AutoModelForCausalLM.from_pretrained("bert-base-spanish-wwm-cased")


def get_chatbot_response(input_text: str) -> str:
    input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors="pt")
    response_ids = model.generate(input_ids, max_length=100, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(response_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)