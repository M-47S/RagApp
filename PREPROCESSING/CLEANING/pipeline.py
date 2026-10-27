# pipeline.py
import os
import sys
import logging
import datetime
import re
from pathlib import Path

from .HTML_Cleaner import clean_html
from .PDF_Cleaner import clean_pdf

logger = logging.getLogger(__name__)

def process_document(file_path: str) -> str:
    """
    Роутер: определяет тип файла по расширению и вызывает нужный клинер.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    logger.info(f"Начата обработка файла: {file_path}")

    if ext in ['.html', '.htm']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_html = f.read()
        return clean_html(raw_html)
        
    elif ext == '.pdf':
        return clean_pdf(file_path)
        
    else:
        logger.error(f"Неподдерживаемый формат файла: {ext}")
        raise ValueError(f"Формат {ext} не поддерживается. Ожидается HTML или PDF.")


def save_to_local_volume(content: str, original_file_path: str) -> str:
    """
    Сохраняет очищенный текст в папку LocalVolume с версионированием.
    Формат имени: {название}_{тип}_{дата}_{номер}.md
    """
    # 1. Настраиваем путь к папке LocalVolume (предполагаем, что скрипт запускается из корня RagApp)
    local_volume_dir = Path("LocalVolume")
    local_volume_dir.mkdir(parents=True, exist_ok=True)

    # 2. Извлекаем имя и тип файла
    file_path_obj = Path(original_file_path)
    original_name = file_path_obj.stem  # Имя без расширения (например, 'university')
    
    ext = file_path_obj.suffix.lower()
    file_type = "HTML" if ext in ['.html', '.htm'] else "PDF"

    # 3. Получаем текущую дату в формате YYYY-MM-DD
    today_date = datetime.date.today().strftime("%Y-%m-%d")

    # 4. Ищем существующие файлы за сегодня, чтобы определить номер
    # Регулярное выражение для поиска файлов: name_TYPE_DATE_NUM.md
    pattern = re.compile(rf"^{re.escape(original_name)}_{file_type}_{today_date}_(\d+)\.md$")
    
    max_number = 0
    for file in local_volume_dir.iterdir():
        if file.is_file():
            match = pattern.match(file.name)
            if match:
                current_num = int(match.group(1))
                if current_num > max_number:
                    max_number = current_num

    # 5. Формируем новое имя файла
    new_number = max_number + 1
    new_filename = f"{original_name}_{file_type}_{today_date}_{new_number}.md"
    output_path = local_volume_dir / new_filename

    # 6. Сохраняем файл
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_path.absolute())


# ==========================================
# БЛОК ДЛЯ ЛОКАЛЬНОГО ТЕСТИРОВАНИЯ
# ==========================================
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    DEFAULT_TEST_FILE = r"C:\Users\0\OneDrive\Desktop\RagApp\testing\universiry.html"

    # Если передан аргумент командной строки — берём его, иначе дефолт
    test_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEST_FILE
    
    print("-" * 50)
    print(f"ТЕСТИРОВАНИЕ CLEANING")
    print(f"Файл: {test_file}")
    print("-" * 50)
    
    try:
        cleaned_md = process_document(test_file)
        
        if cleaned_md:
            print(f"\n✅ УСПЕХ! Очистка завершена.")
            print(f"Длина полученного Markdown: {len(cleaned_md)} символов.")
            
            # Сохраняем в LocalVolume
            saved_path = save_to_local_volume(cleaned_md, test_file)
            
            print(f"💾 Результат сохранен по пути:\n{saved_path}")
            
        else:
            print("\n⚠️ ВНИМАНИЕ: Очистка вернула пустой результат.")
            
    except FileNotFoundError:
        print(f"\n❌ ОШИБКА: Файл не найден по пути {test_file}")
    except Exception as e:
        print(f"\n❌ ОШИБКА при обработке: {e}")
