# PREPROCESSING/CHUNKING/test.py
import sys
import os
import json
import logging
import re
from pathlib import Path
from .chunker import MarkdownChunker

def save_chunks_to_local_volume(collection, md_filename: str) -> str:
    """Сохраняет коллекцию чанков в JSON-файл в LocalVolume с автоинкрементом."""
    local_volume_dir = Path("LocalVolume")
    local_volume_dir.mkdir(parents=True, exist_ok=True)

    # Очищаем имя файла от расширения .md
    base_name = Path(md_filename).stem

    # Ищем существующие файлы для этого документа
    pattern = re.compile(rf"^CHUNKS_{re.escape(base_name)}_(\d+)\.json$")
    max_num = 0
    for file in local_volume_dir.iterdir():
        if file.is_file():
            match = pattern.match(file.name)
            if match:
                max_num = max(max_num, int(match.group(1)))

    # Формируем новое имя
    new_num = max_num + 1
    output_path = local_volume_dir / f"CHUNKS_{base_name}_{new_num}.json"

    # Сериализуем LlamaIndex Nodes в словари (сохраняем связи и метаданные)
    data_to_save = {
        "source_document": md_filename,
        "total_parents": len(collection.parents),
        "total_children": len(collection.children),
        "parents": [node.to_dict() for node in collection.parents],
        "children": [node.to_dict() for node in collection.children]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)

    return str(output_path.absolute())

def main():
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print("❌ Ошибка: Не указан путь к файлу.")
        print("Использование: python -m PREPROCESSING.CHUNKING.test <путь_к_md_файлу>")
        sys.exit(1)

    md_file_path = sys.argv[1]

    if not os.path.exists(md_file_path):
        print(f"❌ Ошибка: Файл не найден по пути {md_file_path}")
        sys.exit(1)

    # Читаем Markdown
    with open(md_file_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    print(f"📄 Загружен документ: {md_file_path}")
    print(f"📏 Размер текста: {len(md_text)} символов.")

    # Инициализируем чанкер (размер 512 токенов, перекрытие 50)
    chunker = MarkdownChunker(chunk_size=512, chunk_overlap=50)

    # Запускаем чанкинг
    print("⚙️  Запуск процесса чанкинга...")
    collection = chunker.chunk(md_text, source_name=os.path.basename(md_file_path))

    print("\n✅ Чанкинг завершен!")
    print(f"📦 Родительских чанков: {len(collection.parents)}")
    print(f"🧩 Дочерних чанков:   {len(collection.children)}")

    # Сохраняем результат
    saved_path = save_chunks_to_local_volume(collection, md_file_path)
    print(f"\n💾 Результат сохранен в:\n{saved_path}")

    # Демонстрация работы связи Small-to-Big (берем случайного ребенка и ищем родителя)
    if collection.children:
        print("\n🔍 Демонстрация Small-to-Big:")
        test_child = collection.children[0]
        parent = collection.get_parent_by_child(test_child)
        
        if parent:
            print(f"   - Взят дочерний чанк (ID: {test_child.node_id[:8]}...). Длина: {len(test_child.text)} симв.")
            print(f"   - Найден его родитель (ID: {parent.node_id[:8]}...). Длина: {len(parent.text)} симв.")
            print(f"   - Родитель содержит текст, начинающийся с: '{parent.text[:100].strip()}...'")

if __name__ == "__main__":
    main()
