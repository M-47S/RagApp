# __init__.py
from .pipeline import process_document

# Определяем, что будет доступно при импорте модуля cleaning
__all__ = ["process_document"]