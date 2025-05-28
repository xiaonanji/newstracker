import requests
from bs4 import BeautifulSoup
from text_summarizer import summarize_text

headers = {'User-Agent': 'Mozilla/5.0'}

def get_webpage_text(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        return text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def main():
    url = 'https://campaignlegal.org/update/elon-musk-has-grown-even-wealthier-through-serving-trumps-administration'
    text = get_webpage_text(url)
    summary = summarize_text(text, topic='Elon Musk')
    print(summary)

if __name__ == "__main__":
    main()