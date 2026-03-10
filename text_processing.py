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

class SemanticExtractor:
    """
    Extracts semantic keywords from a job description using 
    Sentence Transformers (Contextual Embeddings).
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        import torch
        from sentence_transformers import SentenceTransformer
        
        # Determine the best hardware device available
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
            
        self.model = SentenceTransformer(model_name, device=self.device)
        self.forbidden_chars = ["\\", "{", "}", "%", "$", "&", "#", "_", "~", "^"]

    def extract_keywords(self, text: str, top_n: int = 15) -> list[str]:
        """
        Extract the most semantically relevant keywords from the given text
        and ensure they are LaTeX safe.
        """
        from sklearn.feature_extraction.text import CountVectorizer
        from sentence_transformers import util
        import re
        import nltk
        from nltk.corpus import stopwords
        
        # 1. Clean the original text minimally to retain semantic context
        cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        
        # 2. Extract candidate n-grams (1 to 2 words)
        try:
            # Add some custom resume-specific stopwords
            custom_stop_words = list(stopwords.words('english')) + [
                'looking', 'developer', 'experience', 'skills', 'good', 'required', 
                'work', 'team', 'company', 'years', 'using', 'strong', 'ability'
            ]
            vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words=custom_stop_words)
            vectorizer.fit([cleaned_text])
            candidates = vectorizer.get_feature_names_out()
        except ValueError:
            return [] # No words found
            
        if len(candidates) == 0:
            return []
            
        # 3. Create contextual embeddings
        doc_embedding = self.model.encode(cleaned_text, convert_to_tensor=True)
        candidate_embeddings = self.model.encode(candidates, convert_to_tensor=True)
        
        # 4. Calculate cosine similarity
        distances = util.cos_sim(doc_embedding, candidate_embeddings)[0]
        
        # 5. Get top_n candidates
        top_indices = distances.argsort(descending=True)[:top_n]
        top_candidates = [candidates[i] for i in top_indices]
        
        # 6. Apply strictly safe LaTeX filtering
        safe_keywords = []
        for keyword in top_candidates:
            # Strip forbidden characters if any sneaked in
            for char in self.forbidden_chars:
                keyword = keyword.replace(char, "")
            
            keyword = keyword.strip()
            if keyword:
                safe_keywords.append(keyword)
                
        return safe_keywords
