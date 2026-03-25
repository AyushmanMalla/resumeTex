# Resume-TeX

Resume-TeX is a Python-based tool designed to help you tailor your LaTeX resume for specific job applications. It scrapes job descriptions, extracts relevant keywords using state-of-the-art declarative Named Entity Recognition, and seamlessly injects them into your resume, increasing its chances of passing through Applicant Tracking Systems (ATS).

## Current Features

*   **Robust Web Scraping**: Scrapes job descriptions from any given URL using **Playwright**. It handles dynamic content, infinite scrolling, and modern web application structures reliably without manual driver management overhead.
*   **Semantic Entity Extraction**: Uses **GLiNER** (Generalist Model for Named Entity Recognition) to intelligently identify and extract meaningful keywords representing skills (like "programming language", "framework", "tool", "database", and "methodology"). It handles extremely long job descriptions using automated text chunking to prevent token truncation limits.
*   **LaTeX Integration**: Filters out LaTeX-breaking characters and safely injects the extracted keywords into a specified placeholder in your LaTeX resume.
*   **Template-Based**: Comes with a template LaTeX resume to get you started quickly.
*   **Automated Setup Script**: Cross-platform configuration scripts are provided to ensure a reproducible environment with sandboxed dependencies.

## Setup Instructions

To get up and running, use the provided setup scripts to automate virtual environment creation, Python dependency installation, and Playwright browser retrieval.

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
# To activate the environment thereafter:
source .venv/bin/activate
```

**Windows:**
```cmd
setup.bat
:: To activate the environment thereafter:
.venv\Scripts\activate
```

## Usage

Once your environment is activated, run the following command in your terminal:

```bash
python main.py --resume <path-to-your-latex-resume> --url <url-to-your-job>
```

*   `--resume`: Path to your source LaTeX resume (`.tex` file). This file must contain the placeholder `#insert text here`. If not provided, it defaults to `TemplateResume.tex`.
*   `--url`: The URL of the job description to scrape.

The output will be saved automatically as `output.tex` in your directory.

## Core Dependencies

The project maintains a lightweight and focused tech stack:

*   `playwright`: For headless browser automation and robust DOM extraction.
*   `gliner`: For zero-shot semantic Named Entity Recognition and keyword extraction.
*   `nltk`: For text deduplication, stopword removal, and basic token processing.
*   `pytest`: For the local testing suite.
