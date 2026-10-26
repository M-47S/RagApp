# HTML_Cleaner.py
import trafilatura
import ftfy
import logging

logger = logging.getLogger(__name__)

def clean_html(raw_html: str) -> str:
    """
    Извлекает основной контент из HTML и конвертирует в Markdown,
    затем нормализует текст с помощью ftfy.
    """
    if not raw_html:
        return ""

    try:
        # 1. Извлекаем контент и сразу просим Markdown. / отлично отсекает boilerplate (меню, футеры)
        dirty_md = trafilatura.extract(
            raw_html, 
            output_format='markdown',
            include_links=True, 
            include_images=False, # Для RAG картинки пока не нужны
            deduplicate=True      # Включаем встроенную дедупликацию Trafilatura
        )

        if not dirty_md:
            logger.warning("Trafilatura не смогла извлечь контент из HTML.")
            return ""

        # 2. Финальная нормализация (NFKC схлопывает лигатуры и приводит символы к единому виду)
        clean_md = ftfy.fix_text(dirty_md, normalization='NFKC')
        
        return clean_md.strip()

    except Exception as e:
        logger.error(f"Ошибка при очистке HTML: {e}")
        return ""
