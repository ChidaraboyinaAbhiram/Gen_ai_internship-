import re
from typing import Optional


def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the 11-character YouTube video ID from various styles of YouTube URLs.
    
    Supported formats:
    - Standard: https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - Standard (no www): https://youtube.com/watch?v=dQw4w9WgXcQ
    - Shortened: https://youtu.be/dQw4w9WgXcQ
    - Embed: https://www.youtube.com/embed/dQw4w9WgXcQ
    - Shorts: https://www.youtube.com/shorts/dQw4w9WgXcQ
    - Mobile: https://m.youtube.com/watch?v=dQw4w9WgXcQ
    - Query params: https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share
    
    Args:
        url (str): The YouTube URL.
        
    Returns:
        Optional[str]: The 11-character video ID if found, otherwise None.
    """
    if not url:
        return None
        
    url = url.strip()
    
    # Regular expression for YouTube link variations
    # Captures 11 alphanumeric characters (plus - and _) after common prefixes,
    # ensuring they are not followed by any more valid ID characters.
    patterns = [
        r'(?:v=|\/v\/|embed\/|shorts\/|youtu\.be\/|\/embed\/|\/v\/|watch\?v=|&v=)([a-zA-Z0-9_-]{11})(?![a-zA-Z0-9_-])',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    # Fallback: check if the input is itself just a raw 11-character video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
        
    return None


def is_valid_youtube_url(url: str) -> bool:
    """
    Validates if a URL is a syntactically correct YouTube link and contains a valid video ID.
    
    Args:
        url (str): The URL to validate.
        
    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    return extract_video_id(url) is not None
