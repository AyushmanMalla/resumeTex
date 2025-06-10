# parsers/latex_parser.py

import re
from typing import Dict

RESUME_PATH = r"C:\Users\Ayushman\Desktop\CODES\resumeTeX\ayushman_resume.tex" # Replace with the path to your resume file instead

def parse_latex_resume(tex_path: str) -> Dict[str, str]:
    """
    Parses a LaTeX resume and returns a dictionary with sections and their contents.
    """
    with open(tex_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments and LaTeX-specific commands that aren't sectioning
    content = re.sub(r"%.+", "", content)
    content = re.sub(r"\\\\", " ", content)
    content = re.sub(r"\\(textbf|emph|underline|scshape|bfseries|itshape|ttfamily|small|large|huge|normalsize|scriptsize|tiny|textit|texttt)\{([^}]+)\}", r"\2", content)

    # Match sections
    pattern = r"\\begin\{document\}(.*?)\\end\{document\}"
    match = re.search(pattern, content, re.DOTALL)

    content = match.group(1)

    content = re.sub(r'%.*', '', content) # Remove Latex comments
    content = re.sub(r'\\\\|\\newline|\\newpage', '\n', content) # replace \\ and \newline with real newlines
    content = re.sub(r'\\\\|\\newline|\\newpage', '\n', content) # remove environments but keep l;ist items or section text
    content = re.sub(r'\\end\{[a-zA-Z*]+\}', '', content)
    content = re.sub(r'\\[a-zA-Z]+\*?\{(.*?)\}', r'\1', content) # Convert commands with arguments like \textbf{...} -> ...
    content = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?', '', content) # Remove inline commands without arguments like \hfill, \vspace, etc.
    content = re.sub(r'\n\s*\n', '\n', content) # content = re.sub(r'\n\s*\n', '\n', content)
    content = re.sub(r'[ \t]+', ' ', content) #Collpase multiple spaces/newlines
    content = re.sub(r'[ \t]+', ' ', content) # Collapse multiple space/newlines
    print("\n -- Resume Extracted -- \n")

    return content

#UNCOMMENT BELOW FOR INDIVIDUAL TESTING IF REQUIRED

# if __name__ == "__main__":
#     print("\n -- Resume Extracted -- \n")
#     print(parse_latex_resume(RESUME_PATH))