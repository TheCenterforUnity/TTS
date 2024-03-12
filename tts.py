import openai
import pathlib
import os

from pathlib import Path
from openai import OpenAI

# support for the .env file
from dotenv import load_dotenv
load_dotenv()

def sanitize_filename(filename):
    invalid_chars = '/:*?"<>|'
    return ''.join('_' if c in invalid_chars else c for c in filename)


client = OpenAI()

# Test that your OpenAI API key is correctly set as an environment variable
if os.getenv("OPENAI_API_KEY") is not None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print ("OPENAI_API_KEY is ready")
else:
    print ("OPENAI_API_KEY environment variable not found")

# Obtain the filename to record (TXT)
text_file_path = input("Please filename of the text file to record: ")

# Creating audio filename based on first 50 characters of the question
filename = f"{sanitize_filename(text_file_path[:50])}.mp3"
speech_file_path = Path(__file__).parent / filename


# Read the content of the file into a string
with open(text_file_path, 'r', encoding='utf-8') as file:
    text = file.read()

# Now `text` contains the content of your text file as a string
# ... you can use it with your API call
response = client.audio.speech.create(
  model="tts-1-hd",
  voice="onyx",
  input=text
)

response.stream_to_file(speech_file_path)