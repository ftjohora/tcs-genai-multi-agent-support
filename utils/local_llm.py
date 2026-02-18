from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "google/flan-t5-base"

_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def generate(prompt: str, max_new_tokens: int = 256) -> str:
    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = _model.generate(**inputs, max_new_tokens=max_new_tokens)
    return _tokenizer.decode(outputs[0], skip_special_tokens=True)
