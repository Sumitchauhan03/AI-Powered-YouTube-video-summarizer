# Step 1: Import Required Libraries
import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from PIL import Image

# Step 2: Load all the environment variables
load_dotenv()

# Step 3: Configure the Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Step 4: Write a Prompt
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Step 5: Extract Video ID from URL
def extract_video_id(youtube_video_url):
    try:
        if "youtube.com" in youtube_video_url and "v=" in youtube_video_url:
            return youtube_video_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in youtube_video_url:
            return youtube_video_url.split("/")[-1].split("?")[0]
        return None
    except Exception as e:
        st.error(f"Error extracting video ID: {str(e)}")
        return None

# Step 6: Get the transcript data from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            return None

        # Get transcript directly without language handling
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([segment["text"] for segment in transcript_list])

    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None

# Step 7: Generate content using Google Gemini API
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

# Step 8: Build Streamlit Application
st.title("Gemini YouTube Video Summarizer")

# Display YouTube logo
youtube_logo = Image.open("youtube_logo.png")
st.image(youtube_logo, width=150)

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", 
                use_container_width=True)  # Fixed deprecation

if st.button("Get Video Summary"):
    if not youtube_link:
        st.warning("Please enter a YouTube video link")
    else:
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            if summary:
                st.markdown("## Video Summary:")
                st.write(summary)
            else:
                st.error("Summary generation failed")
        else:
            st.error("Failed to extract transcript")