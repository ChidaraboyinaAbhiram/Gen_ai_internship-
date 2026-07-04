import unittest
import sys
import os

# Adjust path to import from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.validators import extract_video_id, is_valid_youtube_url


class TestYouTubeURLParsing(unittest.TestCase):
    def setUp(self):
        # List of valid URLs with expected ID: "dQw4w9WgXcQ"
        self.valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://youtube.com/shorts/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share&t=2",
            "https://youtu.be/dQw4w9WgXcQ?t=15",
            "dQw4w9WgXcQ"  # Raw video ID
        ]
        
        # List of invalid URLs
        self.invalid_urls = [
            "https://www.google.com",
            "https://www.youtube.com",
            "https://youtube.com/watch?v=dQw4w9WgXc",  # 10 chars only
            "https://youtube.com/watch?v=dQw4w9WgXcQ1", # 12 chars
            "https://youtu.be/",                        # No ID
            "",
            "random_string_not_a_url",
            None
        ]

    def test_extract_video_id_valid(self):
        for url in self.valid_urls:
            with self.subTest(url=url):
                video_id = extract_video_id(url)
                self.assertEqual(video_id, "dQw4w9WgXcQ", f"Failed to extract ID from {url}")

    def test_extract_video_id_invalid(self):
        for url in self.invalid_urls:
            with self.subTest(url=url):
                video_id = extract_video_id(url)
                self.assertIsNone(video_id, f"Extracted an ID from invalid url {url}")

    def test_is_valid_youtube_url(self):
        for url in self.valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_valid_youtube_url(url), f"Should be valid: {url}")
                
        for url in self.invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_valid_youtube_url(url), f"Should be invalid: {url}")

if __name__ == '__main__':
    unittest.main()
