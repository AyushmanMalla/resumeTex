import pytest
import sys
from text_processing import GLiNERExtractor

def test_initialization():
    """
    Test that the GLiNERExtractor initializes without crashing.
    """
    extractor = GLiNERExtractor()
    assert extractor.model is not None

def test_semantic_ranking():
    """
    Test that the extractor properly extracts declarative targets (e.g. asking for "programming language" and getting "Python").
    """
    jd_text = "We are looking for a Python developer with experience in Machine Learning and Data Science. Good communication skills required."
    extractor = GLiNERExtractor()
    keywords = extractor.extract_keywords(jd_text, threshold=0.1)
    
    # Python should be extracted based on declarative queries
    lower_keywords = [k.lower() for k in keywords]
    assert "python" in lower_keywords

def test_latex_safety():
    """
    Test that the extractor strips LaTeX breaking characters from the output keywords.
    """
    jd_text = "Experience with C++ \\ { } % $ & # _ ~ ^ and Python."
    extractor = GLiNERExtractor()
    keywords = extractor.extract_keywords(jd_text)
    
    # Assert none of the forbidden characters are in the final keywords array
    forbidden = ["\\", "{", "}", "%", "$", "&", "#", "_", "~", "^"]
    for char in forbidden:
        assert not any(char in keyword for keyword in keywords)
