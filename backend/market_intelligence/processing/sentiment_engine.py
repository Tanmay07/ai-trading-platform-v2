import logging
import torch
from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

logger = logging.getLogger(__name__)

class SentimentEngine:
    """Runs FinBERT inference on news text to generate probability scores."""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.model_name = model_name
        self.device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Loading FinBERT model ({self.model_name}) on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name).to(self.device)
            self.model.eval()
            self.is_ready = True
            logger.info("FinBERT loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load FinBERT: {e}")
            self.is_ready = False

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyzes sentiment and returns probabilities."""
        if not self.is_ready or not text:
            return {"label": "Neutral", "score": 0.0, "confidence": 0.0}
            
        try:
            # FinBERT usually takes up to 512 tokens
            inputs = self.tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            probs = F.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
            
            # ProsusAI/finbert mapping: 0 -> positive, 1 -> negative, 2 -> neutral
            pos_prob, neg_prob, neu_prob = probs[0], probs[1], probs[2]
            
            if pos_prob > neg_prob and pos_prob > neu_prob:
                label = "Positive"
                confidence = float(pos_prob)
                score = float(pos_prob)  # 0 to 1
            elif neg_prob > pos_prob and neg_prob > neu_prob:
                label = "Negative"
                confidence = float(neg_prob)
                score = -float(neg_prob) # -1 to 0
            else:
                label = "Neutral"
                confidence = float(neu_prob)
                score = 0.0
                
            return {
                "label": label,
                "score": round(score, 4),
                "confidence": round(confidence, 4)
            }
        except Exception as e:
            logger.error(f"FinBERT inference error: {e}")
            return {"label": "Neutral", "score": 0.0, "confidence": 0.0}
