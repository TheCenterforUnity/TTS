import openai
import pathlib
import os
from pydub import AudioSegment

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

# Convert the string to a Path object
text_file_path = Path(text_file_path)

# Creating audio filename based on first 50 characters of the question
filename = f"{sanitize_filename(text_file_path.stem[:50])}.mp3"
speech_file_path = Path(__file__).parent / filename


# Read the content of the file into a string
with open(text_file_path, 'r', encoding='utf-8') as file:
    text = file.read()


# Split the text into paragraphs
paragraphs = text.split('\n')

# Initialize variables
buffer = ""
buffer_length = 0
file_counter = 0
text_files = []

# Iterate over paragraphs
for i, paragraph in enumerate(paragraphs):
    paragraph_length = len(paragraph)
    print(f"Processing paragraph {i + 1} of {len(paragraphs)} with length {paragraph_length} characters.")

    if buffer_length + paragraph_length <= 4000:
        # If the paragraph fits in the buffer, add it
        buffer += paragraph + "\n"
        buffer_length += paragraph_length
        print(f"Buffer length is now {buffer_length} characters.")
    else:
        # If the paragraph doesn't fit, write the buffer to a new text file
        buffer_file_path = f"{text_file_path.stem}_{file_counter}.txt"
        with open(buffer_file_path, 'w') as f:
            f.write(buffer)
        text_files.append(buffer_file_path)
        file_counter += 1
        # Start a new buffer with the current paragraph
        buffer = paragraph + "\n"
        buffer_length = paragraph_length

# Don't forget to write the last buffer if it's not empty
if buffer:
    buffer_file_path = f"{text_file_path.stem}_{file_counter}.txt"
    with open(buffer_file_path, 'w') as f:
        f.write(buffer)
    text_files.append(buffer_file_path)

# Now send each text file to the Whisper API and save the audio
audio_files = []
for text_file in text_files:
    with open(text_file, 'r') as f:
        text = f.read()
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="onyx",
        input=text
    )
    print (response)

    audio_file_path = f"{speech_file_path.stem}_{file_counter}{speech_file_path.suffix}"
    response.stream_to_file(audio_file_path)
    audio_files.append(audio_file_path)
    file_counter += 1

# Merge all audio files
combined = AudioSegment.empty()
for audio_file in audio_files:
    combined += AudioSegment.from_mp3(audio_file)

# Save the combined audio
combined.export(speech_file_path, format='mp3')

# Optionally, delete the interim text and audio files
for text_file in text_files:
    os.remove(text_file)
for audio_file in audio_files:
    os.remove(audio_file)