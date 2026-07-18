from typing import Dict, Any, List

class GraphBuilder:
    """
    Maintains a simulated in-memory graph of market relationships.
    """
    def __init__(self):
        # Mock Graph Database relationships
        self.edges = [
            {"source": "TCS.NS", "target": "INFY.NS", "relation": "COMPETES_WITH"},
            {"source": "RELIANCE.NS", "target": "ONGC.NS", "relation": "COMPETES_WITH"},
            {"source": "TCS.NS", "target": "IT_SECTOR", "relation": "PART_OF"},
            {"source": "INFY.NS", "target": "IT_SECTOR", "relation": "PART_OF"},
            {"source": "RELIANCE.NS", "target": "ENERGY_SECTOR", "relation": "PART_OF"},
            {"source": "MACRO_IN", "target": "BANKING_SECTOR", "relation": "INFLUENCES"},
            {"source": "MACRO_IN", "target": "REAL_ESTATE_SECTOR", "relation": "INFLUENCES_NEGATIVELY"}
        ]
        
    def get_related_entities(self, entity: str) -> List[Dict[str, str]]:
        """
        Returns nodes connected to the given entity.
        """
        related = []
        for edge in self.edges:
            if edge["source"] == entity:
                related.append({"entity": edge["target"], "relation": edge["relation"], "direction": "outbound"})
            elif edge["target"] == entity:
                related.append({"entity": edge["source"], "relation": edge["relation"], "direction": "inbound"})
        return related
