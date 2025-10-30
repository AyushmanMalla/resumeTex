import os
import re
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def parse_latex_resume(tex_path: str) -> str:
    """
    Parses a LaTeX file to extract its textual content.

    Args:
        tex_path: The path to the .tex file.

    Returns:
        The extracted text content as a single string.
    """
    try:
        with open(tex_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove comments
        content = re.sub(r"%.*", "", content)
        # Un-escape backslashes
        content = re.sub(r"\\", " ", content)
        # Handle commands with arguments, keeping the argument
        content = re.sub(r"\\[a-zA-Z]+\*?{(.*?)}", r"\1", content)
        # Remove commands without arguments
        content = re.sub(r"\\[a-zA-Z]+\*?(?:\\[^\\]*\])?", '', content)
        # Remove braces
        content = re.sub(r"[{}]", '', content)
        # Remove non-alphanumeric characters (except whitespace)
        content = re.sub(r"[^a-zA-Z0-9\s]", '', content)
        # Normalize whitespace
        content = re.sub(r"\s+", ' ', content).strip()
        return content
    except FileNotFoundError:
        logging.error(f"LaTeX file not found at: {tex_path}")
        return ""
    except Exception as e:
        logging.error(f"Failed to parse LaTeX file: {e}")
        return ""


def inject_keywords(
    latex_path: str,
    injected_text: str,
    placeholder: str = "insert text here"
) -> bool:
    """
    Injects keywords into a LaTeX file and saves it as output.tex.

    Args:
        latex_path: Path to the source LaTeX (.tex) file.
        injected_text: Text to embed in the output file.
        placeholder: The unique marker in the .tex file to be replaced.

    Returns:
        True if injection was successful, False otherwise.
    """
    try:
        with open(latex_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except FileNotFoundError:
        logging.error(f"Could not read source LaTeX file: {latex_path}")
        return False

    if placeholder not in original_content:
        logging.error(f"Placeholder '{placeholder}' not found in {latex_path}.")
        logging.error("Please add the placeholder to your .tex file where you want keywords to be injected.")
        return False

    # Replace the placeholder with the new text
    modified_content = original_content.replace(placeholder, injected_text)

    output_path = "output.tex"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        logging.info(f"Successfully injected keywords into {output_path}")
        return True

    except IOError as e:
        logging.error(f"Failed to write to output file {output_path}: {e}")
        return False