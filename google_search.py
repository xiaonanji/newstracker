"""
Performs a Google search using the Google Custom Search JSON API and displays the results.

This script requires a .env file with the following variables:
1. SEARCH_ENGINE_ID: Your Programmable Search Engine ID (CX)
2. API_KEY: Your Google API Key

Example Usage:
    python google_search.py "cute kittens"

To obtain an API Key:
- Go to the Google Cloud Console (https://console.cloud.google.com/).
- Create a new project or select an existing one.
- Enable the "Custom Search API" in the API Library.
- Go to "Credentials" and create an API key.

To obtain a Search Engine ID (CX):
- Go to the Programmable Search Engine control panel (https://programmablesearchengine.google.com/).
- Create a new search engine.
- Configure it as desired (e.g., specify sites to search).
- The Search Engine ID (CX) will be available on the "Basics" tab of the control panel.
"""
import argparse
import json
import requests
import os
from dotenv import load_dotenv
from youtube_process import is_youtube_video, extract_video_id, get_transcript_with_retry
from text_summarizer import summarize_text
from webpage_process import get_webpage_text

def process_and_summarize(text, source_type="", person_name=""):
    """Process text and generate summary"""
    if text:
        print(f"\n{source_type} Summary:")
        if source_type == "Transcript":
            summary = summarize_text(text, extract_publish_date=False, topic=person_name)
        else:
            summary = summarize_text(text, extract_publish_date=True, topic=person_name)
        print(summary)

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    api_key = os.getenv('API_KEY')
    search_engine_id = os.getenv('SEARCH_ENGINE_ID')
    
    if not api_key or not search_engine_id:
        print("Error: API_KEY and SEARCH_ENGINE_ID must be set in the .env file")
        return

    # Initialize argparse to handle command-line arguments
    parser = argparse.ArgumentParser(
        description="Search for recent public activities of a person.",
        epilog="Example: python google_search.py \"Elon Musk\""
    )
    parser.add_argument("name", help="The person's full name (e.g., \"Elon Musk\").")
    args = parser.parse_args()

    # Build the search query
    query = f"{args.name} recent public activities in last 3 months"

    # Google Custom Search API endpoint
    url = "https://www.googleapis.com/customsearch/v1"
    # Parameters for the API request
    params = {
        "key": api_key,  # API Key from environment variable
        "cx": search_engine_id,  # Programmable Search Engine ID from environment variable
        "q": query  # The search query
    }

    try:
        # Make the GET request to the API with a 10-second timeout
        response = requests.get(url, params=params, timeout=10)

        # Check for specific HTTP client error codes before attempting to parse JSON
        # These errors usually indicate issues with the request parameters or API key.
        if response.status_code == 400:  # Bad Request
            # Attempt to get more details from the API's JSON error response
            error_details = response.json().get("error", {}).get("message", "No specific error message from API.")
            print(f"Error: Bad request to API (Status Code 400). This might be due to an invalid Search Engine ID or a malformed query.")
            print(f"API Error Message: {error_details}")
            return # Exit after handling the error
        elif response.status_code == 401:  # Unauthorized
             error_details = response.json().get("error", {}).get("message", "No specific error message from API.")
             print(f"Error: Unauthorized request (Status Code 401). Please check your API key.")
             print(f"API Error Message: {error_details}")
             return # Exit after handling the error
        elif response.status_code == 403:  # Forbidden
            error_details = response.json().get("error", {}).get("message", "No specific error message from API.")
            print(f"Error: Forbidden request (Status Code 403). This could be an API key issue, or the API may not be enabled for your project, or lack of permissions for the search engine.")
            print(f"API Error Message: {error_details}")
            return # Exit after handling the error
        elif response.status_code == 429:  # Too Many Requests
            error_details = response.json().get("error", {}).get("message", "No specific error message from API.")
            print(f"Error: API query limit exceeded (Status Code 429). Please check your quota in the Google Cloud Console.")
            print(f"API Error Message: {error_details}")
            return # Exit after handling the error

        # For other HTTP errors (e.g., 5xx server errors), raise an HTTPError exception
        response.raise_for_status()
        
        # Parse the JSON response
        search_results = response.json()

        # Check if 'items' key exists and has content
        if "items" in search_results and len(search_results["items"]) > 0:
            print("\nSearch Results:")
            for item in search_results["items"]:
                url = item.get('link', 'N/A')
                # Debug print to see the item structure
                # print("\nItem structure:")
                # print(json.dumps(item, indent=2))
                
                # Get timestamp based on content type
                pagemap = item.get('pagemap', {})
                if 'videoobject' in pagemap:
                    timestamp = pagemap['videoobject'][0].get('datepublished', 'N/A')
                else:
                    timestamp = (
                        pagemap.get('metatags', [{}])[0].get('article:published_time') or
                        pagemap.get('metatags', [{}])[0].get('og:updated_time') or
                        pagemap.get('metatags', [{}])[0].get('date') or
                        pagemap.get('article', [{}])[0].get('datepublished') or
                        'N/A'
                    )
                
                print(f"\nURL: {url}")
                print(f"Published: {timestamp}")
                
                if is_youtube_video(item):
                    print("Youtube video")
                    video_id = extract_video_id(item.get('link', ''))
                    if video_id:
                        transcript = get_transcript_with_retry(video_id)
                        process_and_summarize(transcript, "Transcript", args.name)
                else:
                    print("Not a Youtube video")
                    text = get_webpage_text(item.get('link', ''))
                    process_and_summarize(text, "Webpage Content", args.name)
                
                # title = item.get('title', 'N/A')
                # link = item.get('link', 'N/A')
                # snippet = item.get('snippet', 'N/A')
                # print(f"\nTitle: {title}")
                # print(f"Link: {link}")
                # print(f"Snippet: {snippet}")
                print("-" * 40)
        else:
            # Handle cases where 'items' might be missing or empty,
            # or if the API returns a specific error message within a successful (e.g., 200 OK) response.
            if "error" in search_results: # API returned a 200 OK but with an error message in the body
                error_message = search_results.get("error", {}).get("message", "No specific error message from API.")
                print(f"API returned an error: {error_message}")
            elif "spelling" in search_results.get("searchInformation", {}): # API suggests a spelling correction
                 corrected_query = search_results["searchInformation"]["spelling"]["correctedQuery"]
                 print(f"No results found. Did you mean: {corrected_query}?")
            else: # General no results found
                print("No results found for your query.")

    # Handle network-related errors
    except requests.exceptions.Timeout:
        print("Error: The request timed out. The server might be busy or there could be network connectivity issues.")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the Google API. Please check your internet connection and DNS settings.")
    # Handle other exceptions related to the request
    except requests.exceptions.HTTPError as e: # Handles errors raised by response.raise_for_status()
        print(f"HTTP error occurred: {e}")    
    except requests.exceptions.RequestException as e: 
        print(f"An error occurred while making the API request: {e}")
    # Handle errors in parsing JSON
    except json.JSONDecodeError:
        # This can happen if the server returns non-JSON output (e.g., HTML error page on some client errors not caught above)
        print("Error: Could not parse the API response. The response was not in valid JSON format.")
        print(f"Raw response snippet (first 200 chars): {response.text[:200] if response else 'No response object'}")
    # Catch any other unexpected errors
    except Exception as e: 
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
