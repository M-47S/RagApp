# structs.py
from typing import List, Dict
from llama_index.core.schema import TextNode, NodeRelationship

class ChunkCollection:
    """
    Контейнер для хранения результатов чанкинга.
    Разделяет родительские и дочерние чанки для удобства.
    """
    def __init__(self):
        self.parents: List[TextNode] = []
        self.children: List[TextNode] = []

        # Словарь для мгновенного поиска родителя по ID: {parent_id: TextNode}
        self._parent_map: Dict[str, TextNode] = {}

    def add_parent(self, node: TextNode):
        self.parents.append(node)
        self._parent_map[node.node_id] = node

    def add_children(self, nodes: List[TextNode]):
        self.children.extend(nodes)

    def get_parent_by_child(self, child_node: TextNode) -> TextNode | None:
        """Возвращает родительский чанк для заданного дочернего."""
        # Достаем связь PARENT из метаданных связей LlamaIndex
        parent_rel = child_node.relationships.get(NodeRelationship.PARENT)
        if parent_rel:
            return self._parent_map.get(parent_rel.node_id)
        return None

    def __len__(self) -> int:
        return len(self.children)
