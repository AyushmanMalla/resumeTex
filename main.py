import argparse
import os
import sys
from scraper import selenium_scrape_job_description
from text_processing import preprocess_text_for_ats
from tex_tools import inject_keywords

#Usage: python main.py --resume <path-to-your-latex-resume (will default to template if none provided)> --url <url-to-your-job>

def main():
    """
    Main function to run the ATS resume optimization process.
    """
    parser = argparse.ArgumentParser(
        description="Scrape a job description, extract keywords, and inject them into a LaTeX resume.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--resume",
        type=str,
        help="Path to your source LaTeX resume (.tex file).\nThis file must contain the placeholder '#insert text here'.",
        default="TemplateResume.tex"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The URL of the job description to scrape."
    )
    args = parser.parse_args()

    if not os.path.exists(args.resume):
        print(f"Error: The specified resume file does not exist: {args.resume}", file=sys.stderr)
        sys.exit(1)

    # 1. Scrape job description
    print(f"Scraping job description from: {args.url}")
    job_description_text = selenium_scrape_job_description(args.url)

    if not job_description_text:
        print("\nFailed to retrieve job description. Aborting.", file=sys.stderr)
        sys.exit(1)

    # 2. Preprocess text to get keywords
    print("\nExtracting semantic keywords using Sentence Transformers...")
    from text_processing import SemanticExtractor
    extractor = SemanticExtractor()
    ats_keywords_list = extractor.extract_keywords(job_description_text)
    
    if not ats_keywords_list:
        print("\nNo keywords were extracted after processing. Aborting.", file=sys.stderr)
        sys.exit(1)
        
    ats_keywords = " ".join(ats_keywords_list)
    print(f"Extracted {len(ats_keywords_list)} top semantic keywords.")

    # 3. Inject keywords into new .tex file
    print("\nInjecting keywords into new LaTeX file...")
    success = inject_keywords(
        latex_path=args.resume,
        injected_text=ats_keywords
    )

    if success:
        print("\nProcess completed successfully!")
        print(f"Find your new resume content in: output.tex")
        sys.exit(0)
    else:
        print("\nProcess failed. Please check the error messages above.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
