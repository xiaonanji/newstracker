import requests
import json
import argparse
import hashlib  # Import hashlib for generating URL hash
from webpage_process import get_webpage_text
from text_summarizer import summarize_text
from database import write_to_database  # Import the database writing function
from firebase_admin import db  # Import db for checking existing records

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Fetch and summarize news articles.")
    parser.add_argument('-q', '--query', type=str, required=True, help="Search query for news articles")
    args = parser.parse_args()

    person = args.query.replace(' ', '_')  # Replace spaces with underscores for the database key

    # Use the query argument in the URL
    url = (f'https://newsapi.org/v2/everything?'
           f'q={args.query}&'
           f'from=2025-04-27&'
           f'sortBy=popularity&'
           f'apiKey=3aa6f510cfa34745b858d33aa1af02c4')

    response = requests.get(url)
    articles = response.json().get('articles', [])  # Get the articles array from the JSON response

    for article in articles:
        print('=' * 50)
        article_url = article.get('url')  # Extract the URL of the article
        if article_url:
            # Generate a unique hash for the URL
            url_id = hashlib.md5(article_url.encode()).hexdigest()

            print(f"Title: {article.get('title', 'No title available')}")
            print(f"Published at: {article.get('publishedAt', 'No publish date available')}")

            # Check if the url_id already exists in the database
            ref = db.reference(f"{person}/{url_id}")
            existing_data = ref.get()
            if existing_data is not None:
                print(f"Skipping article with URL: {article_url} (already exists in the database)")
                print(f"Summary from database:\n{existing_data.get('summary', 'No summary available')}\n")
                continue
            
            # Extract text from the webpage
            article_text = get_webpage_text(article_url)
            if article_text:
                # Summarize the extracted text
                summary = summarize_text(article_text, extract_publish_date=False, topic=args.query)
                print(f"Summary:\n{summary}\n")

                # Prepare data for the database
                data = {
                    url_id:
                    {
                        'title': article.get('title', 'No title available'),
                        'url': article.get('url', 'No URL available'),
                        'published_at': article.get('publishedAt', 'No publish date available'),
                        'summary': summary
                    }
                }

                # Write the data to the database
                write_to_database(person, data)
            else:
                print("Failed to extract text from the webpage.\n")

if __name__ == '__main__':
    main()