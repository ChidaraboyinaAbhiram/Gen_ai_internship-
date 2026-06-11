# utils/prompts.py
PROMPTS = {
    "blog": {
        "system": "You are an expert content writer and SEO specialist.",
        "user": """Write a {length}-word blog post about: {topic}
Target audience: {audience}
Tone: {tone}
SEO Keywords to include: {keywords}
Structure: Engaging title, introduction, {sections} sections, conclusion.

Format with markdown headings.""",
    },
    "email": {
        "system": "You are an expert professional email writer.",
        "user": """Write a {purpose} email.
Recipient: {recipient}
Sender context: {context}
Tone: {tone}
Include: Subject line, greeting, body, call-to-action, sign-off.""",
    },
    "social": {
        "system": "You are a viral social media content creator.",
        "user": """Create a {platform} post about: {topic}
Brand: {brand}
Tone: {tone}
Include hashtags: {use_hashtags}
Include emojis: {use_emoji}
Platform limit: {char_limit} characters.""",
    },
    "ad": {
        "system": "You are an award-winning advertising copywriter.",
        "user": """Write compelling ad copy for: {product}
Unique selling point: {usp}
Target audience: {audience}
Platform: {platform}
Call to action: {cta}
Tone: {tone}
Return: Headline, subheadline, body copy, CTA button text.""",
    },
}
