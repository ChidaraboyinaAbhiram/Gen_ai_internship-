import unittest
import sys
import os

# Adjust path to import from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.prompts import build_summarization_prompt

class TestPromptGeneration(unittest.TestCase):
    def setUp(self):
        self.sample_transcript = "[00:10] Introduction to Python coding. [01:15] Variables and data types are fundamental concepts."
        self.sample_title = "Python for Beginners"
        
        # Exact expected headers in markdown prompt template
        self.expected_headings = [
            "# Video Title",
            "## Executive Summary",
            "## Detailed Summary",
            "## Timeline Summary",
            "## Key Takeaways",
            "## Technical Concepts",
            "## Actionable Insights",
            "## 5-Minute Revision Notes",
            "## 5 MCQs with Answers",
            "## Difficulty Level",
            "## Keywords"
        ]

    def test_prompt_contains_all_headings(self):
        styles = [
            "Short Summary",
            "Detailed Summary",
            "Bullet Notes",
            "Academic Notes",
            "Beginner Friendly",
            "Interview Preparation",
            "Exam Revision"
        ]
        
        for style in styles:
            with self.subTest(style=style):
                prompt = build_summarization_prompt(
                    transcript=self.sample_transcript,
                    style=style,
                    title=self.sample_title
                )
                
                # Check that each expected markdown heading is explicitly requested in the template
                for heading in self.expected_headings:
                    self.assertIn(
                        heading, 
                        prompt, 
                        f"Prompt template for style '{style}' is missing expected heading: {heading}"
                    )

if __name__ == '__main__':
    unittest.main()
