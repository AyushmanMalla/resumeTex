import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from scraper import *
from LatexResume_parser import *

# Ensure necessary NLTK data is available
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Compile regex patterns for efficiency
LATEX_CMD_PATTERN = re.compile(r"\\[A-Za-z]+")
BRACE_PATTERN = re.compile(r"[{}]")
NON_ALPHANUM_PATTERN = re.compile(r"[^a-zA-Z0-9\s]")
MULTI_SPACE_PATTERN = re.compile(r"\s+")

# Load English stopwords
STOP_WORDS = set(stopwords.words('english'))


def preprocess_text(text: str) -> str:
    """
    Clean and normalize a document string:
      1. Remove LaTeX commands (e.g., \section, \textbf)
      2. Strip braces { }
      3. Remove non-alphanumeric characters
      4. Lowercase
      5. Tokenize and remove stopwords
      6. Return cleaned string of tokens joined by spaces
    """
    # Step 1: Remove LaTeX commands
    cleaned = LATEX_CMD_PATTERN.sub(' ', text)
    # Step 2: Remove braces
    cleaned = BRACE_PATTERN.sub(' ', cleaned)
    # Step 3: Remove non-alphanumeric chars
    cleaned = NON_ALPHANUM_PATTERN.sub(' ', cleaned)
    # Step 4: Normalize whitespace
    cleaned = MULTI_SPACE_PATTERN.sub(' ', cleaned)
    # Step 5: Lowercase
    cleaned = cleaned.lower().strip()

    # Step 6: Tokenize
    tokens = word_tokenize(cleaned)
    # Remove stopwords and tokens of length <=1
    filtered_tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

    return ' '.join(filtered_tokens)


def preprocess_documents(resume_text: str, jd_text: str) -> tuple:
    """
    Preprocess both resume and job description texts.

    Returns:
        resume_clean: preprocessed resume string
        jd_clean: preprocessed job description string
    """
    resume_clean = preprocess_text(resume_text)
    jd_clean = preprocess_text(jd_text)
    return resume_clean, jd_clean


if __name__ == '__main__':
    # Example usage
    sample_resume = parse_latex_resume(r"C:\Users\Ayushman\Desktop\CODES\resumeTeX\ayushman_resume.tex")
    # sample_jd = selenium_scrape_job_description("https://jobs.bytedance.com/en/position/7377543090393139507/detail")
    sample_jd = selenium_scrape_job_description("https://blackrock.wd1.myworkdayjobs.com/en-US/BlackRock_Professional/job/Vice-President--ServiceNow-Architect_R253208-1")
    r_clean, j_clean = preprocess_documents(sample_resume, sample_jd)
    print('Resume:', r_clean)
    print('Job Desc:', j_clean)
