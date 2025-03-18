# Step 1: Import Required Libraries
import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from dotenv import load_dotenv
from PIL import Image
import requests
import random

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

        try:
            # First attempt: direct transcript retrieval
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([segment["text"] for segment in transcript_list])
        except Exception as first_error:
            st.warning("Direct transcript access failed. Attempting with proxy...")
            
            # Get free proxies from public proxy list (for demo purposes)
            # In production, consider using a paid proxy service
            try:
                # Use a free proxy list API (you might want to replace this with a more reliable source)
                proxies = get_free_proxies()
                
                if proxies:
                    # Try with proxies
                    for proxy in proxies[:5]:  # Try first 5 proxies
                        try:
                            transcript_list = YouTubeTranscriptApi.get_transcript(
                                video_id,
                                proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'}
                            )
                            return " ".join([segment["text"] for segment in transcript_list])
                        except Exception as proxy_error:
                            continue
                
                # If all proxies fail, show error
                raise Exception("All proxy attempts failed. YouTube might be blocking transcript access.")
            except Exception as e:
                raise Exception(f"Failed to access transcript: {str(e)}")

    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None

# Function to get free proxies (for demonstration purposes)
def get_free_proxies():
    try:
        # This is a simple example - consider using a more reliable proxy source in production
        response = requests.get('https://free-proxy-list.net/')
        
        # Very basic parsing - in production, use a more robust method
        proxies = []
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            tbody = soup.find('tbody')
            for tr in tbody.find_all('tr')[:20]:  # Get first 20 proxies
                tds = tr.find_all('td')
                ip = tds[0].text
                port = tds[1].text
                if tds[6].text.lower() == 'yes':  # Check if HTTPS
                    proxies.append(f"{ip}:{port}")
        
        # Fallback to a few hardcoded proxies if web scraping fails
        if not proxies:
            # These are example proxies and may not work - replace with actual working proxies
            proxies = [
                "203.30.189.31:80",
                "51.159.115.233:3128",
                "148.76.97.250:80"
            ]
        
        return proxies
    except:
        # Fallback to a few hardcoded proxies
        return [
            "203.30.189.31:80",
            "51.159.115.233:3128",
            "148.76.97.250:80"
        ]

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

st.markdown("""
### Note on Transcript Access
Some videos may be unavailable for transcript extraction due to:
- Region restrictions
- YouTube IP blocking
- Creator disabled captions
- Private/unlisted videos without captions
""")

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
        with st.spinner("Extracting transcript and generating summary..."):
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                if summary:
                    st.markdown("## Video Summary:")
                    st.write(summary)
                else:
                    st.error("Summary generation failed")
            else:
                st.error("Failed to extract transcript. This may be due to YouTube restrictions or the video doesn't have captions.")