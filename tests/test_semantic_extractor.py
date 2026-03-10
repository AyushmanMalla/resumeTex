import pytest
import sys
from text_processing import SemanticExtractor

def test_device_initialization():
    """
    Test that the SemanticExtractor initializes without crashing
    and correctly assigns a fallback device (cpu, cuda, or mps).
    """
    extractor = SemanticExtractor()
    assert extractor.device in ["cpu", "cuda", "mps"]
    assert extractor.model is not None

def test_semantic_ranking():
    """
    Test that the extractor properly ranks relevant technical skills 
    higher than generic filler words using cosine similarity.
    """
    jd_text = "We are looking for a Python developer with experience in Machine Learning and Data Science. Good communication skills required."
    extractor = SemanticExtractor()
    keywords = extractor.extract_keywords(jd_text, top_n=3)
    
    # Python or machine learning should be extracted as top keywords, filler words like 'we' or 'good' should not
    lower_keywords = [k.lower() for k in keywords]
    assert any(expected in lower_keywords for expected in ["python", "machine learning", "data science"])
    assert "good" not in lower_keywords
    assert "we" not in lower_keywords

def test_latex_safety():
    """
    Test that the extractor strips LaTeX breaking characters from the output keywords.
    """
    jd_text = "Experience with C++ \\ { } % $ & # _ ~ ^ and Python."
    extractor = SemanticExtractor()
    keywords = extractor.extract_keywords(jd_text, top_n=5)
    
    # Assert none of the forbidden characters are in the final keywords array
    forbidden = ["\\", "{", "}", "%", "$", "&", "#", "_", "~", "^"]
    for char in forbidden:
        assert not any(char in keyword for keyword in keywords)
