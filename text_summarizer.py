import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def summarize_text(text, extract_publish_date=False, topic=None):
    """
    Summarizes the given text using OpenAI's GPT-4 model.
    
    Args:
        text (str): The text to summarize
        topic (str, optional): Specific topic to focus on in the summary. Defaults to None.
    
    Returns:
        str: The generated summary or None if an error occurs
    """
    # Initialize OpenAI with API key from environment
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OPENAI_API_KEY must be set in the .env file")

    # Truncate text to approximately 8000 tokens (roughly 6000 words)
    words = text.split()
    if len(words) > 3000:
        text = ' '.join(words[:3000])
        print("Note: Text was truncated to fit within token limits")
        # print(f"truncated: {text}")

    try:
        # Prepare the prompt based on whether a specific topic is provided
        prompt = "Please provide a comprehensive summary of the following text:"
        if topic:
            if extract_publish_date:
                prompt = f"Please extract the publish date of the text and provide a summary related to {topic} from the following text, using two languages, English and Chinese:"
            else:
                prompt = f"Please provide a summary related to {topic} from the following text, using two languages, English and Chinese:"

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 for longer context length
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates detailed summaries of text. Focus on the main points and key information while maintaining important details."},
                {"role": "user", "content": f"{prompt}\n\n{text}"}
            ],
            max_tokens=500,  # Adjusted to stay within context length limit
            temperature=0.3  # Lower temperature for more focused summaries
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None 