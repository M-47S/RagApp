# helpers.py
from typing import Dict, Any
from llama_index.core.schema import TextNode, NodeRelationship

def format_node_for_debug(node: TextNode) -> Dict[str, Any]:
    """Превращает TextNode в словарь для красивого вывода."""
    data = {
        "id": node.node_id,
        "content_preview": node.get_content()[:150] + "...",
        "metadata": node.metadata,
        "parent_id": None
    }
    
    # Проверяем наличие родителя
    if NodeRelationship.PARENT in node.relationships:
        data["parent_id"] = node.relationships[NodeRelationship.PARENT].node_id
        
    return data
