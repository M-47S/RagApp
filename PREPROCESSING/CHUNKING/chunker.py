# Chunker.py
import logging
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import NodeRelationship, RelatedNodeInfo
from .structs import ChunkCollection

logger = logging.getLogger(__name__)

class MarkdownChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.md_parser = MarkdownNodeParser()
        self.text_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk(self, markdown_text: str, source_name: str = "unknown") -> ChunkCollection:
        collection = ChunkCollection()

        if not markdown_text.strip():
            logger.warning("Получен пустой Markdown документ.")
            return collection

        doc = Document(text=markdown_text, metadata={"source": source_name})

        # Шаг 1: Получаем РОДИТЕЛЬСКИЕ чанки (по заголовкам)
        logger.info("Запуск MarkdownNodeParser...")
        parent_nodes = self.md_parser.get_nodes_from_documents([doc])
        
        for parent in parent_nodes:
            collection.add_parent(parent)

            # Шаг 2: Режем КАЖДЫЙ родительский чанк на дочерние
            # Передаем [parent], чтобы сплиттер работал только с ним
            child_nodes = self.text_splitter.get_nodes_from_documents([parent])

            for child in child_nodes:
                # Шаг 3: Связываем дочерний чанк с родительским
                child.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(
                    node_id=parent.node_id
                )
                
                # Копируем метаданные (заголовки) от родителя к детям
                child.metadata.update(parent.metadata)
                
                # Добавляем в коллекцию
                collection.add_children([child])

            # Связываем родителя с его детьми (опционально, для полноты)
            parent.relationships[NodeRelationship.CHILD] = [
                RelatedNodeInfo(node_id=child.node_id) for child in child_nodes
            ]

        logger.info(f"Создано {len(collection.parents)} родительских и {len(collection.children)} дочерних чанков.")
        return collection
