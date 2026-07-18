import logging
from typing import List, Dict, Any
from portfolio.constraints.portfolio_constraints import PortfolioConstraint

logger = logging.getLogger("PortfolioOptimizer")

class PortfolioOptimizer:
    """
    Constraint-Based Optimization Framework for Portfolio Construction.
    Takes a list of candidates and a list of constraints, and iteratively selects
    the optimal portfolio that satisfies all rules.
    """
    def __init__(self, constraints: List[PortfolioConstraint]):
        self.constraints = constraints
        
    def optimize(self, candidates: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns (selected_positions, rejected_positions)
        """
        logger.info(f"Optimizing portfolio from {len(candidates)} candidates using {len(self.constraints)} constraints.")
        
        # Sort candidates by intrinsic quality first (our primary objective to maximize)
        sorted_candidates = sorted(
            candidates, 
            key=lambda x: (x.get('trade_quality_prediction', 50) + x.get('classification_probability', 0.5) * 100), 
            reverse=True
        )
        
        selected = []
        rejected = []
        
        for cand in sorted_candidates:
            # Check all constraints
            violations = []
            for constraint in self.constraints:
                if not constraint.check_candidate(cand, selected):
                    violations.append(constraint.get_rejection_reason())
                    
            if not violations:
                selected.append(cand)
            else:
                cand['rejection_reasons'] = violations
                rejected.append(cand)
                
        logger.info(f"Optimization complete: {len(selected)} selected, {len(rejected)} rejected.")
        return selected, rejected
