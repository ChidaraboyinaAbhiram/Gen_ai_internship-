from typing import Dict

# Dictionary defining the tone, structure, and requirements for each summary style
STYLE_PROMPTS: Dict[str, str] = {
    "Short Summary": (
        "Focus on delivering a high-level, extremely concise overview. In the Detailed Summary section, "
        "condense the material into a maximum of 2-3 brief paragraphs covering only the most essential "
        "core messages and conclusions. Keep explanations brief and highly focused."
    ),
    "Detailed Summary": (
        "Focus on deep coverage and extensive explanation. In the Detailed Summary section, do a thorough "
        "deep-dive. Elaborate on every major argument, supporting detail, case study, or example mentioned "
        "in the transcript. Ensure no valuable technical detail is omitted."
    ),
    "Bullet Notes": (
        "Format the Detailed Summary section strictly using a clean, structured hierarchical bullet-point list. "
        "Use bullet points (`-`) and sub-bullets to represent relationships between concepts. Avoid long paragraphs. "
        "Make it highly scannable and easy to review."
    ),
    "Academic Notes": (
        "Format the summary as a formal academic paper or textbook chapter summary. Use precise, technical terminology "
        "and objective academic tone. In the Detailed Summary, highlight the underlying theories, frameworks, methodology, "
        "and literature contexts. Define key terminology with rigor."
    ),
    "Beginner Friendly": (
        "Explain complex technical concepts using simple, plain language, analogies, and everyday terms. Avoid "
        "dense technical jargon unless you immediately explain it with a concrete example. The tone should be "
        "welcoming, encouraging, and easy to grasp for someone with zero background knowledge."
    ),
    "Interview Preparation": (
        "Tailor the Detailed Summary and Key Takeaways to focus on professional applicability, system design, core algorithms, "
        "or industry practices. In the revision notes, emphasize common interview questions, architectural trade-offs, "
        "and optimal solutions related to the video content."
    ),
    "Exam Revision": (
        "Structure the Detailed Summary and Revision Notes to optimize for active recall and exam readiness. Focus "
        "on definitions, equations, key dates, names, formulas, and sequential steps. Organize content in a logical "
        "progression that matches learning objectives, highlighting high-yield facts."
    )
}

def get_system_instruction() -> str:
    """
    Returns the core system prompt setting up rules, constraint boundaries, and output expectations.
    """
    return (
        "You are a Senior Python AI Engineer, Educator, and expert summarizer. Your task is to analyze "
        "the provided transcript of a YouTube video and produce comprehensive study notes. \n\n"
        "CRITICAL RULES:\n"
        "1. STRICTLY ignore all greetings, channel intros, sponsor messages, advertisements, calls to subscribe/like/share, "
        "filler words, repetitions, and non-educational chit-chat.\n"
        "2. PRESERVE technical accuracy and keep chronological flow where applicable.\n"
        "3. NEVER hallucinate facts, statistics, names, or URLs. Only use information directly stated or clearly implied "
        "within the transcript. If a specific section cannot be generated because the information isn't in the transcript, "
        "output a brief, factual explanation instead of inventing details.\n"
        "4. Output must be in PURE Markdown. Do not wrap the entire output in a markdown block (e.g. ```markdown ... ```).\n"
        "5. You MUST include exactly the 13 sections specified in the prompt, using the exact headers provided."
    )

def build_summarization_prompt(transcript: str, style: str, title: str) -> str:
    """
    Combines the system instruction, style specific prompt, and transcript data
    to create a single structured prompt for the LLM.
    
    Args:
        transcript (str): The formatted transcript text (optionally with timestamps).
        style (str): The summary style chosen by the user.
        title (str): The video title.
        
    Returns:
        str: The complete prompt for the LLM.
    """
    style_instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["Detailed Summary"])
    
    prompt = f"""
{get_system_instruction()}

---
## Video Context
- **Title**: {title}
- **Requested Note Style**: {style}

## Style Guidelines for this request:
{style_instruction}

---
## Output Structure:
You must output exactly these 11 sections with the exact headers listed below. Keep the headings exactly as written here:

# Video Title
(Display the title: "{title}")

## Executive Summary
(Provide a brief, high-level summary of 1-2 paragraphs summarizing the core message and purpose of the video.)

## Detailed Summary
(Generate the comprehensive summary. Make sure to adhere to the requested note style: "{style}".)

## Timeline Summary
(If the transcript contains timestamp tags like `[MM:SS]` or `[HH:MM:SS]`, create a chronological timeline of key topics discussed, highlighting the start time and a summary of that section. Format as a table or bulleted list with times. If no timestamps are present in the transcript, write "No timestamps available for this video.")

## Key Takeaways
(List 5-7 core lessons, insights, or findings as a bulleted list.)

## Technical Concepts
(List and explain key terms, tools, algorithms, or concepts introduced in the video. Format as `- **Concept Name**: Explanation`.)

## Actionable Insights
(Provide a list of steps, recommendations, or actions that a viewer could implement based on the video.)

## 5-Minute Revision Notes
(Write highly condensed summary notes for quick recall, focusing on key facts and core definitions.)

## 5 MCQs with Answers
(Create 5 multiple choice questions. Format:
Question 1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
**Correct Answer**: [A/B/C/D]
**Explanation**: [Brief explanation]
)

## Difficulty Level
(Specify either: Beginner, Intermediate, or Advanced. Provide a 1-2 sentence justification based on the concepts covered.)

## Keywords
(Provide exactly 10 comma-separated key terms or phrases representing the video.)

---
## YouTube Video Transcript:
{transcript}
"""
    return prompt
