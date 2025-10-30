# Resume-TeX

Resume-TeX is a Python-based tool designed to help you tailor your LaTeX resume for specific job applications. It scrapes job descriptions, extracts relevant keywords, and seamlessly injects them into your resume, increasing its chances of passing through Applicant Tracking Systems (ATS).

## Current Features

*   **Web Scraping**: Scrapes job descriptions from any given URL using Selenium. It's robust, with multiple fallback strategies to handle different website structures.
*   **Keyword Extraction**: Processes the scraped text to identify and extract meaningful keywords. It filters out stop words and irrelevant characters.
*   **LaTeX Integration**: Injects the extracted keywords into a specified placeholder in your LaTeX resume.
*   **Template-Based**: Comes with a template LaTeX resume to get you started quickly.

## Future Features

*   **Semantic Keyword Matching**: Instead of just syntactic matching, use word embeddings (like Word2Vec or GloVe) or transformer-based models (like BERT) to find semantically similar keywords between the job description and your resume.
*   **Resume Content Suggestion**: Suggest skills or experiences to add to your resume based on the job description.
*   **Cover Letter Generation**: Automatically generate a draft cover letter based on the job description and your resume.
*   **GUI**: A simple graphical user interface to make the tool more user-friendly.

## Usage

To use Resume-TeX, run the following command in your terminal:

```bash
python main.py --resume <path-to-your-latex-resume> --url <url-to-your-job>
```

*   `--resume`: Path to your source LaTeX resume (.tex file). This file must contain the placeholder `insert text here`. If not provided, it defaults to `TemplateResume.tex`.
*   `--url`: The URL of the job description to scrape.

## Dependencies

The project uses the following libraries:

*   requests>=2.31.0
*   beautifulsoup4>=4.12.0
*   transformers>=4.30.0
*   torch>=2.0.0
*   numpy>=1.24.0
*   scikit-learn>=1.0.0
*   spacy>=3.5.0
*   nltk>=3.8.0
*   sentence-transformers>=2.2.0
*   selenium
