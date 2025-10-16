# app.py
import streamlit as st
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for the AI
prompt = """You are a YouTube video summarizer. You will summarize the transcript text
and provide the important points in under 250 words. Please provide the summary of the text given here:  """

# Helper: Extract video ID from any YouTube URL
def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")

# Get transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = get_video_id(youtube_video_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([t["text"] for t in transcript_list])
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound):
        st.error("Transcript not available for this video.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# Generate summary using Google Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = get_video_id(youtube_link)
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    except ValueError:
        st.warning("Invalid YouTube URL entered.")

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
    else:
        st.warning("Cannot generate summary without transcript.")




