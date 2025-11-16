import requests
import hashlib
from webpage_process import get_webpage_text
from text_summarizer import summarize_text
from database import write_to_database
from firebase_admin import db
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse

def main():
    parser = argparse.ArgumentParser(description="Fetch and summarize news articles for persons.")
    parser.add_argument('-n', '--name', type=str, help="Process only this person's name (optional)")
    args = parser.parse_args()

    # Get today's date and the same day last month
    today = datetime.today()
    from_date = (today - relativedelta(months=1)).strftime('%Y-%m-%d')

    if args.name:
        # Only process the specified person
        person_name = args.name
        person_id = person_name.replace(' ', '_')
        persons = {person_id: {"name": person_name}}
    else:
        # Fetch all persons from the database
        persons_ref = db.reference("persons")
        persons = persons_ref.get()
        if not persons:
            print("No persons found in the database.")
            return

    for person_id, person_info in persons.items():
        person_name = person_info.get("name", person_id)
        print(f"\nProcessing news for: {person_name}")

        url = (f'https://newsapi.org/v2/everything?'
               f'q="{person_name}"&'
               f'from={from_date}&'
               f'sortBy=popularity&'
               f'apiKey=3aa6f510cfa34745b858d33aa1af02c4')

        response = requests.get(url)
        articles = response.json().get('articles', [])

        print(f"Found {len(articles)} articles for {person_name}.")

        for article in articles:
            print('=' * 50)
            article_url = article.get('url')
            if article_url:
                url_id = hashlib.md5(article_url.encode()).hexdigest()
                ref = db.reference(f"{person_id}/{url_id}")
                existing_data = ref.get()
                if existing_data is not None:
                    print(f"Skipping article with URL: {article_url} (already exists in the database)")
                    print(f"Summary from database:\n{existing_data.get('summary', 'No summary available')}\n")
                    continue

                article_text = get_webpage_text(article_url)
                if article_text:
                    summary = summarize_text(article_text, extract_publish_date=False, topic=person_name)
                    print(f"Summary:\n{summary}\n")

                    data = {
                        url_id: {
                            'title': article.get('title', 'No title available'),
                            'url': article.get('url', 'No URL available'),
                            'published_at': article.get('publishedAt', 'No publish date available'),
                            'summary': summary
                        }
                    }
                    write_to_database(person_id, data)
                else:
                    print("Failed to extract text from the webpage.\n")

if __name__ == '__main__':
    main()