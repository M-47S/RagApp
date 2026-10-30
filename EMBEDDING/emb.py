from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. Настройки ---
LOCAL_PATH = r".\EMBEDDING\model\multilingual-e5-large"

embed_model = HuggingFaceEmbedding(
    model_name=LOCAL_PATH, # Теперь передаем путь к скачанной папке
    device="cpu"           # или "cuda", если есть видеокарта
)
print("Model is ready")