from typing import Dict, Any, List
from event_intelligence.knowledge_graph.graph_builder import GraphBuilder

class ImpactEstimator:
    """
    Uses the Knowledge Graph to propagate event impact to related entities.
    """
    def __init__(self):
        self.graph = GraphBuilder()
        
    def estimate_impact(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimates first and second-order impact of the event.
        """
        primary_company = event.get("company", "UNKNOWN")
        significance = event.get("significance_score", 50)
        
        impact = {
            "primary_impact": {
                "entity": primary_company,
                "sentiment": "Positive" if "Win" in event.get("event_type", "") or "Surprise" in event.get("event_type", "") else "Negative",
                "magnitude": significance
            },
            "secondary_impact": []
        }
        
        # Propagate through the graph
        related = self.graph.get_related_entities(primary_company)
        
        for r in related:
            sec_impact = {
                "entity": r["entity"],
                "relation_path": r["relation"]
            }
            
            # Simple rule-based propagation for MVP
            if r["relation"] == "COMPETES_WITH":
                sec_impact["sentiment"] = "Negative" if impact["primary_impact"]["sentiment"] == "Positive" else "Positive"
                sec_impact["magnitude"] = round(significance * 0.4, 1) # Competitors feel 40% inverse impact
            elif r["relation"] == "PART_OF":
                sec_impact["sentiment"] = impact["primary_impact"]["sentiment"]
                sec_impact["magnitude"] = round(significance * 0.2, 1) # Sector feels 20% direct impact
            elif r["relation"] == "INFLUENCES_NEGATIVELY":
                sec_impact["sentiment"] = "Negative"
                sec_impact["magnitude"] = round(significance * 0.8, 1) 
            else:
                sec_impact["sentiment"] = "Neutral"
                sec_impact["magnitude"] = round(significance * 0.1, 1)
                
            impact["secondary_impact"].append(sec_impact)
            
        event["estimated_impact"] = impact
        return event
