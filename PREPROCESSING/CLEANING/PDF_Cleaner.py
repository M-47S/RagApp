# PDF_Cleaner.py
import pymupdf4llm
import ftfy
import difflib
import logging

logger = logging.getLogger(__name__)

def _deduplicate_lines(markdown_text: str, similarity_threshold: float = 0.9) -> str:
    """
    Удаляет почти идентичные строки (например, колонтитулы) с помощью difflib.
    """
    lines = markdown_text.split('\n')
    unique_lines = []
    
    # Храним последние N строк для сравнения, чтобы не сравнивать каждую строку со всем документом
    # (колонтитулы обычно повторяются каждые 1-2 страницы)
    history_window = 50 

    for line in lines:
        stripped_line = line.strip()
        
        # Пропускаем пустые строки (оставляем один перенос для форматирования)
        if not stripped_line:
            if unique_lines and unique_lines[-1] != "":
                unique_lines.append("")
            continue

        is_duplicate = False
        # Сравниваем текущую строку с недавними уникальными строками
        for seen_line in unique_lines[-history_window:]:
            if not seen_line: continue
            
            # SequenceMatcher вычисляет коэффициент схожести (0.0 до 1.0)
            matcher = difflib.SequenceMatcher(None, stripped_line, seen_line)
            if matcher.ratio() > similarity_threshold:
                is_duplicate = True
                break
                
        if not is_duplicate:
            unique_lines.append(stripped_line)
            
    return '\n'.join(unique_lines)

def clean_pdf(pdf_path: str) -> str:
    """
    Извлекает текст из PDF в формате Markdown, нормализует кодировку и удаляет дубликаты.
    """
    try:
        # 1. Извлечение в Markdown (PyMuPDF4LLM сам пытается найти таблицы и структуру)
        # Возвращает "грязный" Markdown
        dirty_md = pymupdf4llm.to_markdown(pdf_path)
        
        if not dirty_md:
            return ""

        # 2. Исправляем возможные "кракозябры" из PDF шрифтов
        fixed_md = ftfy.fix_text(dirty_md, normalization='NFKC')

        # 3. Дедупликация (удаление повторяющихся колонтитулов)
        clean_md = _deduplicate_lines(fixed_md)
        
        return clean_md.strip()

    except Exception as e:
        logger.error(f"Ошибка при очистке PDF {pdf_path}: {e}")
        return ""