import pytest
from unittest.mock import MagicMock
from market_intelligence.processing.deduplicator import Deduplicator
from market_intelligence.processing.company_tagger import CompanyTagger
from market_intelligence.processing.event_classifier import EventClassifier
from market_intelligence.scoring.news_importance import NewsImportanceScorer
from market_intelligence.memory.market_memory_engine import MarketMemoryEngine

def test_deduplicator_hash():
    d = Deduplicator()
    hash1 = d.generate_hash("Q3 Results", "NSE", "2024-01-01T10:00:00Z")
    hash2 = d.generate_hash("Q3 Results", "NSE", "2024-01-01T10:00:00Z")
    hash3 = d.generate_hash("Q3 Results", "BSE", "2024-01-01T10:00:00Z")
    
    assert hash1 == hash2
    assert hash1 != hash3

def test_company_tagger():
    tagger = CompanyTagger()
    text = "Reliance Industries announced strong Q3 results. TCS also performed well."
    
    tags = tagger.tag_companies(text)
    assert "RELIANCE" in tags
    assert "TCS" in tags
    assert "INFY" not in tags

def test_event_classifier():
    classifier = EventClassifier()
    assert classifier.classify("Strong Quarterly Results announced today") == "Earnings"
    assert classifier.classify("Company wins large order from Defense") == "Business"
    assert classifier.classify("RBI increases interest rates") == "Macro"
    assert classifier.classify("We are happy to announce") == "General"

def test_news_importance_scorer():
    scorer = NewsImportanceScorer()
    
    # High impact (NSE + Earnings + High Confidence)
    score_high = scorer.score("NSE Announcements", "Earnings", 0.95)
    assert score_high > 80
    
    # Low impact (Google News + General + Low Confidence)
    score_low = scorer.score("Google News Business", "General", 0.4)
    assert score_low < 50

def test_market_memory_engine():
    engine = MarketMemoryEngine()
    
    context = engine.get_historical_context("BEL", "Business", "Positive")
    assert context is not None
    assert context["success_rate_pct"] == 78
    assert context["avg_t7_return_pct"] == 8.6
    
    insight = engine.generate_insight_text("BEL", "Business", context)
    assert "8.6%" in insight
    assert "78%" in insight
    
    # Neutral events shouldn't trigger a hard context match
    neutral = engine.get_historical_context("BEL", "Business", "Neutral")
    assert neutral is None
