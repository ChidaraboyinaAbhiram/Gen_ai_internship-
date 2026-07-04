import re
from typing import List, Optional, Tuple
import requests
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

def fetch_video_title(video_id: str) -> str:
    """
    Scrapes the YouTube page to extract the video title.
    Falls back to a default format if scraping fails or is blocked.
    
    Args:
        video_id (str): The 11-character YouTube video ID.
        
    Returns:
        str: The extracted video title, or a fallback title.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Check og:title meta tag first as it's cleaner
            og_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', response.text)
            if og_match:
                # Decode HTML entities if any
                title = og_match.group(1)
                return html_decode(title)
                
            # Fallback to <title> tag
            title_match = re.search(r"<title>(.*?)</title>", response.text)
            if title_match:
                title = title_match.group(1)
                # Remove " - YouTube" suffix
                title = re.sub(r"\s*-\s*YouTube\s*$", "", title, flags=re.IGNORECASE)
                return html_decode(title)
    except Exception:
        pass
        
    return f"YouTube Video ({video_id})"

def html_decode(s: str) -> str:
    """
    Decodes basic HTML entities commonly found in scraped page titles.
    """
    s = s.replace("&amp;", "&")
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&quot;", '"')
    s = s.replace("&#39;", "'")
    return s

def _convert_to_dicts(fetched_data) -> List[dict]:
    """
    Converts a list of FetchedTranscriptSnippet objects (v1.2.4+) or standard objects
    into standard dictionaries for backwards compatibility.
    """
    if not fetched_data:
        return []
    if isinstance(fetched_data[0], dict):
        return fetched_data
    return [
        {
            "text": getattr(item, "text", ""),
            "start": getattr(item, "start", 0.0),
            "duration": getattr(item, "duration", 0.0)
        }
        for item in fetched_data
    ]

def _get_session_with_cookies() -> Optional[requests.Session]:
    """
    Loads Netscape formatted session cookies from cookies.txt (if present)
    to authenticate requests and bypass YouTube IP bans or rate limits.
    """
    import os
    import http.cookiejar
    
    cookies_path = "cookies.txt"
    if not os.path.exists(cookies_path):
        return None
    try:
        session = requests.Session()
        cookie_jar = http.cookiejar.MozillaCookieJar(cookies_path)
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        session.cookies.update(cookie_jar)
        return session
    except Exception as e:
        # Fail silently but print warning
        print(f"Warning: Failed to load cookies.txt: {e}")
        return None

def fetch_transcript(video_id: str) -> Tuple[Optional[List[dict]], Optional[str]]:
    """
    Downloads the transcript for a given YouTube video ID.
    Prioritizes:
      1. English (manual or auto-generated)
      2. Auto-translated to English
      3. Any first available transcript
      
    Args:
        video_id (str): The YouTube video ID.
        
    Returns:
        Tuple[Optional[List[dict]], Optional[str]]:
            - List of transcript entries (with 'text', 'start', 'duration') if successful, else None.
            - Error message string if failed, else None.
    """
    try:
        session = _get_session_with_cookies()
        api = YouTubeTranscriptApi(proxy_config=None, http_client=session)
        transcript_list = api.list(video_id)
        
        # Try to find a manual or auto English transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
            return _convert_to_dicts(transcript.fetch()), None
        except NoTranscriptFound:
            pass
            
        # Try to find other common transcripts, or auto-translated to English
        try:
            first_transcript = next(iter(transcript_list))
            if first_transcript.is_translatable:
                translated = first_transcript.translate('en')
                return _convert_to_dicts(translated.fetch()), None
        except Exception:
            pass
            
        # Fallback: get the first available raw transcript (in whatever language it's in)
        try:
            first_transcript = next(iter(transcript_list))
            return _convert_to_dicts(first_transcript.fetch()), None
        except StopIteration:
            return None, "No transcripts available in any language for this video."
            
    except TranscriptsDisabled:
        return None, "Transcripts are disabled or unavailable for this video."
    except VideoUnavailable:
        return None, "This YouTube video is unavailable or does not exist."
    except Exception as e:
        error_msg = str(e)
        if "block" in error_msg.lower() or "ip" in error_msg.lower() or "cookie" in error_msg.lower():
            instructions = (
                "YouTube is blocking requests from this IP address.\n\n"
                "💡 **How to bypass this block:**\n"
                "1. Install a browser extension like **'Get cookies.txt LOCALLY'** (Chrome/Firefox).\n"
                "2. Open YouTube in your browser, log in (if not already), click the extension, and export your cookies as a Netscape-format text file.\n"
                "3. Save the exported file as **`cookies.txt`** in the project's root folder:\n"
                "   `C:\\Users\\Abhiram\\Desktop\\3rd_internship\\youtube-transcript-summarizer\\cookies.txt`\n"
                "4. Run the summarization again. The app will automatically load your cookies to authenticate requests!"
            )
            return None, instructions
        return None, f"Failed to retrieve transcript: {error_msg}"

def format_seconds(seconds: float) -> str:
    """
    Converts seconds (float) into MM:SS or HH:MM:SS format.
    """
    secs = int(seconds)
    hrs = secs // 3600
    mins = (secs % 3600) // 60
    secs = secs % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    else:
        return f"{mins:02d}:{secs:02d}"

def format_transcript(transcript_list: List[dict], include_timestamps: bool = True) -> str:
    """
    Formats the raw transcript list into a readable text block.
    
    Args:
        transcript_list (List[dict]): The raw transcript data.
        include_timestamps (bool): Whether to prepend timestamps (e.g. [01:23]).
        
    Returns:
        str: The formatted transcript.
    """
    if not transcript_list:
        return ""
        
    if include_timestamps:
        lines = []
        for entry in transcript_list:
            timestamp = format_seconds(entry['start'])
            # Clean newlines from text entries to prevent visual fragmentation
            text = entry['text'].replace('\n', ' ').strip()
            lines.append(f"[{timestamp}] {text}")
        return "\n".join(lines)
    else:
        # Reconstruct transcript as a clean continuous paragraph block
        words = [entry['text'].replace('\n', ' ').strip() for entry in transcript_list]
        text = " ".join(words)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
