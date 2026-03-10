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

    def extract_keywords(self, text: str, top_n: int = 15, diversity: float = 0.7) -> list[str]:
        """
        Extract the most semantically relevant keywords from the given text
        and ensure they are LaTeX safe. Leverages MMR to reduce redundancy.
        """
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        import re
        import nltk
        from nltk.corpus import stopwords
        
        # 1. Clean the original text minimally to retain semantic context
        # Fix missing spaces from bad scraping (e.g. CamelCase concatenated strings)
        cleaned_text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", " ", cleaned_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        
        # 2. Extract candidate n-grams (1 to 2 words)
        try:
            vectorizer = CountVectorizer(ngram_range=(1, 2))
            vectorizer.fit([cleaned_text])
            raw_candidates = vectorizer.get_feature_names_out()
            
            # Add some custom resume-specific stopwords
            custom_stop_words = set(stopwords.words('english')) | {
                'looking', 'developer', 'experience', 'skills', 'good', 'required', 
                'work', 'team', 'company', 'years', 'using', 'strong', 'ability',
                'responsibilities', 'qualifications', 'requirements', 'role',
                'build', 'develop', 'improve', 'working', 'knowledge'
            }
            
            # Filter candidates so they don't start/end/are stopwords
            candidates = []
            for cand in raw_candidates:
                words = cand.split()
                if len(words) == 1 and words[0] in custom_stop_words:
                    continue
                if len(words) == 2 and (words[0] in custom_stop_words or words[1] in custom_stop_words):
                    continue
                candidates.append(cand)
                
        except ValueError:
            return [] # No words found
            
        if len(candidates) == 0:
            return []
            
        # 3. Create contextual embeddings
        doc_embedding = self.model.encode([cleaned_text]) # 1 x D
        candidate_embeddings = self.model.encode(candidates) # N x D
        
        # 4. Calculate similarities
        doc_sims = cosine_similarity(candidate_embeddings, doc_embedding).flatten()
        cand_sims = cosine_similarity(candidate_embeddings, candidate_embeddings)
        
        # 5. Maximal Marginal Relevance (MMR)
        selected_idx = [np.argmax(doc_sims)]
        unselected_idx = list(range(len(candidates)))
        unselected_idx.remove(selected_idx[0])
        
        for _ in range(top_n - 1):
            if not unselected_idx: 
                break
                
            best_score = -10
            best_i = -1
            
            for i in unselected_idx:
                sim_to_doc = doc_sims[i]
                sim_to_selected = max([cand_sims[i][j] for j in selected_idx])
                
                score = (1 - diversity) * sim_to_doc - diversity * sim_to_selected
                if score > best_score:
                    best_score = score
                    best_i = i
                    
            selected_idx.append(best_i)
            unselected_idx.remove(best_i)
            
        top_candidates = [candidates[i] for i in selected_idx]
        
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
