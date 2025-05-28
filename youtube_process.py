from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
import os
import time
from dotenv import load_dotenv
from text_summarizer import summarize_text

def is_youtube_video(item):
    # Check if the link is a YouTube URL
    link = item.get('link', '')
    if 'youtube.com/watch' in link or 'youtu.be/' in link:
        return True

    # Check the pagemap for videoobject
    pagemap = item.get('pagemap', {})
    video_objects = pagemap.get('videoobject', [])
    for video in video_objects:
        embed_url = video.get('embedurl', '')
        content_url = video.get('contenturl', '')
        if 'youtube.com/embed/' in embed_url or 'youtube.com/watch' in content_url:
            return True

    # Check the displayLink
    display_link = item.get('displayLink', '')
    if 'youtube.com' in display_link or 'youtu.be' in display_link:
        return True

    return False

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY must be set in the .env file")

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_video_metadata(video_id):
    """
    Retrieves metadata for a given YouTube video ID.
    """
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    )
    response = request.execute()
    if response['items']:
        item = response['items'][0]
        snippet = item['snippet']
        statistics = item['statistics']
        metadata = {
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'published_at': snippet.get('publishedAt'),
            'channel_title': snippet.get('channelTitle'),
            'view_count': statistics.get('viewCount'),
            'like_count': statistics.get('likeCount'),
            'comment_count': statistics.get('commentCount')
        }
        return metadata
    else:
        return None

def get_transcript(video_id, languages=['en']):
    """
    Retrieves the transcript for a given YouTube video ID.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(languages)
        formatter = TextFormatter()
        return formatter.format_transcript(transcript.fetch())
    except Exception as e:
        print(f"Transcript not available: {e}")
        return None
    
def get_transcript_with_retry(video_id, languages=['en'], retries=3, delay=1):
    for attempt in range(retries):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript = transcript_list.find_transcript(languages)
            except:
                transcript = transcript_list.find_generated_transcript(languages)

            formatter = TextFormatter()
            return formatter.format_transcript(transcript.fetch())
        except Exception as e:
            print(f"Attempt {attempt+1}: {e}")
            time.sleep(delay)
    print("Transcript not available after retries.")
    return None

def main():
    # Example YouTube video URL
    video_url = 'https://www.youtube.com/watch?v=hycoCYenXls'
    
    video_id = extract_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL.")
        return

    # print(f"Video ID: {video_id}")
    # metadata = get_video_metadata(video_id)
    # if metadata:
    #     print("Video Metadata:")
    #     for key, value in metadata.items():
    #         print(f"{key.capitalize()}: {value}")
    # else:
    #     print("Failed to retrieve video metadata.")

    transcript = get_transcript_with_retry(video_id)
    if transcript:
        print("\nTranscript:")
        print(transcript)
        summary = summarize_text(transcript, topic="Elon Musk")
        print("\nSummary:")
        print(summary)
    else:
        print("Transcript not available.")

if __name__ == "__main__":
    main()