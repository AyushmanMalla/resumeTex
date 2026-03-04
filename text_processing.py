import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def _download_nltk_data_if_needed():
    """Downloads required NLTK data if not already present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except:
        print("Punkt not found! Downloading NLTK 'punkt' model...")
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except:
        print("Stopwords not found! Downloading NLTK 'stopwords'...")
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('punkt_tab')
    except:
        print("punkt_tab not found! Downloading NLTK 'punkt_tab'...")
        nltk.download('punkt_tab')

# Ensure data is available on import
_download_nltk_data_if_needed()

# Pre-compile regex patterns for efficiency
LATEX_CMD_PATTERN = re.compile(r"\\[A-Za-z]+")
BRACE_PATTERN = re.compile(r"[{}]")
NON_ALPHANUM_PATTERN = re.compile(r"[^a-zA-Z0-9\s]")
MULTI_SPACE_PATTERN = re.compile(r"\s+")

STOP_WORDS = set(stopwords.words('english'))

def preprocess_text_for_ats(text: str) -> str:
    """
    Cleans and preprocesses a string of text to extract keywords for ATS.

    This involves removing special characters, LaTeX commands, and common stop words.

    Args:
        text: The input string (e.g., from a job description).

    Returns:
        A string of space-separated keywords.
    """
    # Remove LaTeX commands and braces
    cleaned = LATEX_CMD_PATTERN.sub(' ', text)
    cleaned = BRACE_PATTERN.sub(' ', cleaned)
    
    # Remove non-alphanumeric characters
    cleaned = NON_ALPHANUM_PATTERN.sub(' ', cleaned)
    
    # Normalize whitespace
    cleaned = MULTI_SPACE_PATTERN.sub(' ', cleaned).strip()

    # Tokenize and filter out stop words and short tokens
    tokens = word_tokenize(cleaned.lower())
    filtered_tokens = [
        token for token in tokens if token not in STOP_WORDS and len(token) > 1
    ]
    
    return ' '.join(filtered_tokens)
