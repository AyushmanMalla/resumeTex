import os
import re
import subprocess
import argparse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from scraper import *  # Ensure this exists and works

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# --------- Preprocessing Utilities ---------
LATEX_CMD_PATTERN = re.compile(r"\\[A-Za-z]+")
BRACE_PATTERN = re.compile(r"[{}]")
NON_ALPHANUM_PATTERN = re.compile(r"[^a-zA-Z0-9\s]")
MULTI_SPACE_PATTERN = re.compile(r"\s+")

STOP_WORDS = set(stopwords.words('english'))

def preprocess_text(text: str) -> str:
    """Preprocess a string for ATS injection."""
    cleaned = LATEX_CMD_PATTERN.sub(' ', text)
    cleaned = BRACE_PATTERN.sub(' ', cleaned)
    cleaned = NON_ALPHANUM_PATTERN.sub(' ', cleaned)
    cleaned = MULTI_SPACE_PATTERN.sub(' ', cleaned)

    tokens = word_tokenize(cleaned)
    filtered_tokens = [t for t in tokens if t.lower() not in STOP_WORDS and len(t) > 1]
    return ' '.join(filtered_tokens)


# --------- Resume Parser (LaTeX .tex) ---------
def parse_latex_resume(tex_path: str) -> str:
    with open(tex_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r"%.+", "", content)
    content = re.sub(r"\\\\", " ", content)
    content = re.sub(r"\\[a-zA-Z]+\*?\{(.*?)\}", r"\1", content)
    content = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", '', content)
    content = re.sub(r"[{}]", '', content)
    content = re.sub(r"[^a-zA-Z0-9\s]", '', content)
    content = re.sub(r"\s+", ' ', content)
    return content


# --------- Injection and Compilation ---------
def inject_text_and_compile(
    latex_path: str,
    injected_text: str,
    placeholder: str = "#insert text here"
):
    """
    Injects text into a LaTeX file, compiles it, then restores the original file.
    
    Args:
        latex_path: Path to the LaTeX (.tex) file with placeholder
        injected_text: Text to invisibly embed in the PDF
        output_pdf_path: Path to save the compiled PDF
        placeholder: Unique marker in the LaTeX file
    """
    # Read original LaTeX
    with open(latex_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    # Replace placeholder
    modified_lines = [
        line.replace(placeholder, injected_text) for line in original_lines
    ]



    with open("output.tex", 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)



    # Restore original LaTeX file
    with open(latex_path, 'w', encoding='utf-8') as f:
        f.writelines(original_lines)

    print("\n")
    print(f"------------- [SUCCESS] ----------------")
    print("Output succesfully saved!")
    print("\n")

# --------- CLI Entry ---------
def main():
    parser = argparse.ArgumentParser(description="Inject ATS-optimized keywords into LaTeX resume.")
    parser.add_argument("--resume", type=str, required=True, help="Path to your LaTeX resume (.tex)")
    parser.add_argument("--url", type=str, required=True, help="Job description URL")
    args = parser.parse_args()

    # Scrape and preprocess JD
    raw_jd = selenium_scrape_job_description(args.url)
    injection = preprocess_text(raw_jd)

    inject_text_and_compile(
        latex_path=args.resume,
        injected_text=injection
    )


if __name__ == "__main__":
    main()
