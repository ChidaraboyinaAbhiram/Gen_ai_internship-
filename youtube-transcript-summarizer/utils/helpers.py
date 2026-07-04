import re

def count_words(text: str) -> int:
    """
    Counts the number of words in a text block.
    
    Args:
        text (str): The input text.
        
    Returns:
        int: Word count.
    """
    if not text:
        return 0
    # Clean up markdown tags, replace them with spaces for accurate word count
    clean_text = re.sub(r'[#*`_\[\]\(\)\-\|]', ' ', text)
    words = clean_text.split()
    return len(words)

def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """
    Estimates the reading time in minutes for a given text.
    Assumes average reading speed of 200 words per minute.
    Always returns at least 1 minute if the text is not empty.
    
    Args:
        text (str): The input text.
        wpm (int): Words per minute reading rate.
        
    Returns:
        int: Estimated reading time in minutes.
    """
    words = count_words(text)
    if words == 0:
        return 0
    minutes = round(words / wpm)
    return max(1, minutes)

def parse_markdown_sections(content: str) -> dict:
    """
    Parses a single unified study notes markdown text block and splits it
    into individual sections based on heading indicators (e.g. '## Executive Summary').
    
    Args:
        content (str): The raw markdown string.
        
    Returns:
        dict: A dictionary mapping section header names to their corresponding contents.
    """
    sections = {}
    if not content:
        return sections
        
    headers = [
        "Executive Summary",
        "Detailed Summary",
        "Timeline Summary",
        "Key Takeaways",
        "Important Quotes",
        "Technical Concepts",
        "Actionable Insights",
        "5-Minute Revision Notes",
        "5 MCQs with Answers",
        "5 MCQs with answers",
        "10 Flashcards",
        "Difficulty Level",
        "Keywords"
    ]
    
    lines = content.split('\n')
    current_header = "Intro"
    current_content = []
    
    for line in lines:
        matched_header = None
        # Check if line matches a header (starts with # or ##)
        if line.startswith("## ") or line.startswith("# "):
            clean_line = line.replace("#", "").strip()
            # Check which header name it matches
            for h in headers:
                if h.lower() in clean_line.lower():
                    matched_header = h
                    break
                    
        if matched_header:
            # Store previous section content
            if current_content:
                sections[current_header] = "\n".join(current_content).strip()
            # Normalize key variations
            normalized_header = matched_header
            if "mcq" in matched_header.lower():
                normalized_header = "5 MCQs with Answers"
            current_header = normalized_header
            current_content = []
        else:
            current_content.append(line)
            
    # Store the remaining content
    if current_content:
        sections[current_header] = "\n".join(current_content).strip()
        
    return sections

def parse_mcqs(mcq_text: str) -> list:
    """
    Parses MCQ raw text into a list of structured dictionaries.
    Handles typical LLM multiple-choice formatting.
    
    Args:
        mcq_text (str): Raw text content containing the MCQs.
        
    Returns:
        list: List of dicts with 'question', 'options' (dict), 'correct', 'explanation'.
    """
    mcqs = []
    if not mcq_text:
        return mcqs
        
    # Split by Question marker
    blocks = re.split(r'\b(?:Question|Q)\s*\d+\s*[:.]\s*', mcq_text)
    
    for block in blocks:
        if not block.strip():
            continue
            
        # 1. Parse Question Text (everything up to option A)
        q_match = re.search(r'^(.*?)(?=\s*\n+\s*[A-D]\))', block, re.DOTALL)
        if not q_match:
            continue
        question = q_match.group(1).strip()
        
        # 2. Parse Options
        a_match = re.search(r'\bA\)\s*(.*?)(?=\n+\s*B\))', block, re.DOTALL)
        b_match = re.search(r'\bB\)\s*(.*?)(?=\n+\s*C\))', block, re.DOTALL)
        c_match = re.search(r'\bC\)\s*(.*?)(?=\n+\s*D\))', block, re.DOTALL)
        # Option D is followed by Correct Answer or Explanation
        d_match = re.search(r'\bD\)\s*(.*?)(?=\n+\s*(?:Correct Answer|Correct|\*\*Correct))', block, re.DOTALL)
        if not d_match:
            d_match = re.search(r'\bD\)\s*(.*?)(?=\n+\s*Explanation)', block, re.DOTALL)
        if not d_match:
            # Fallback if nothing else follows option D in the block
            d_match = re.search(r'\bD\)\s*(.*)$', block, re.DOTALL)
            
        a = a_match.group(1).strip() if a_match else ""
        b = b_match.group(1).strip() if b_match else ""
        c = c_match.group(1).strip() if c_match else ""
        d = d_match.group(1).strip() if d_match else ""
        
        # 3. Parse Correct Answer Letter
        ans_match = re.search(r'(?:Correct Answer|Correct|Answer)\s*[:.-]*\s*([A-D])', block, re.IGNORECASE)
        correct_answer = ans_match.group(1).strip().upper() if ans_match else ""
        
        # 4. Parse Explanation
        exp_match = re.search(r'(?:Explanation)\s*[:.-]*\s*(.*)$', block, re.DOTALL | re.IGNORECASE)
        explanation = exp_match.group(1).strip() if exp_match else ""
        # Strip markdown syntax
        explanation = re.sub(r'^[\s*#:-]+', '', explanation)
        explanation = re.sub(r'[\s*]+$', '', explanation)
        
        mcqs.append({
            "question": question,
            "options": {"A": a, "B": b, "C": c, "D": d},
            "correct": correct_answer,
            "explanation": explanation
        })
        
    return mcqs

def parse_flashcards(flashcard_text: str) -> list:
    """
    Parses flashcard bullet points into a list of structured dicts.
    Handles typical LLM outputs with or without Front/Back and numbering prefixes.
    Format: Front: ... | Back: ...
    
    Args:
        flashcard_text (str): Raw text content containing the flashcards.
        
    Returns:
        list: List of dicts with 'front', 'back'.
    """
    cards = []
    if not flashcard_text:
        return cards
        
    lines = flashcard_text.split('\n')
    for line in lines:
        line = line.strip().lstrip('-* ').strip()
        if not line:
            continue
            
        # Split by pipe separator
        parts = line.split('|')
        if len(parts) >= 2:
            front = parts[0]
            back = parts[1]
        else:
            # Fallback if they are separated by "Back:" string instead of pipe
            split_back = re.split(r'\bBack\b\s*[:.-]*\s*', line, flags=re.IGNORECASE)
            if len(split_back) == 2:
                front = split_back[0]
                back = split_back[1]
            else:
                continue
                
        # Clean both front and back
        front = front.replace("**", "")
        back = back.replace("**", "")
        
        # Remove Front: and Back: prefixes case-insensitively
        front = re.sub(r'\bFront\b\s*[:.-]*\s*', '', front, flags=re.IGNORECASE)
        back = re.sub(r'\bBack\b\s*[:.-]*\s*', '', back, flags=re.IGNORECASE)
        
        # Remove leading numbers/bullets (e.g. "1. ", "10. ", "- ")
        front = re.sub(r'^(?:\d+\s*[\s.:-]\s*|[-*]\s*)', '', front).strip()
        back = re.sub(r'^(?:\d+\s*[\s.:-]\s*|[-*]\s*)', '', back).strip()
        
        if front or back:
            cards.append({
                "front": front,
                "back": back
            })
            
    return cards

def sanitize_for_pdf(text: str) -> str:
    """
    Sanitizes Unicode characters to standard Latin-1/ASCII characters
    to prevent FPDF2 encoding crashes when using standard Helvetica/Arial fonts.
    Replaces common typographic unicode symbols and strips unsupported characters.
    
    Args:
        text (str): Raw string with potential unicode symbols.
        
    Returns:
        str: Sanitized, PDF-friendly ASCII/Latin-1 string.
    """
    if not text:
        return ""
        
    # Replace common typographic characters with ASCII equivalents
    replacements = {
        "\u201c": '"',  # Left smart double quote
        "\u201d": '"',  # Right smart double quote
        "\u2018": "'",  # Left smart single quote
        "\u2019": "'",  # Right smart single quote
        "\u2013": "-",  # En-dash
        "\u2014": "-",  # Em-dash
        "\u2022": "*",  # Bullet symbol
        "\u2026": "...",# Ellipsis
        "\u00a0": " ",  # Non-breaking space
        "\u2122": "TM", # Trademark
        "\u00ae": "(R)",# Registered
        "\u00a9": "(C)",# Copyright
    }
    
    for uni, asc in replacements.items():
        text = text.replace(uni, asc)
        
    # Filter character by character. FPDF2 standard fonts support character codes 0 to 255.
    sanitized_chars = []
    for char in text:
        code = ord(char)
        if code <= 255:
            sanitized_chars.append(char)
        else:
            # Handle some specific non-Latin-1 symbols gracefully
            if code in (0x2713, 0x2714):   # Checkmarks
                sanitized_chars.append("[Yes]")
            elif code == 0x2717:           # Cross mark
                sanitized_chars.append("[No]")
            elif code == 0x2192:           # Right arrow ->
                sanitized_chars.append("->")
            elif code == 0x2190:           # Left arrow <-
                sanitized_chars.append("<-")
            else:
                # Discard or substitute emojis and other characters
                sanitized_chars.append(" ")
                
    # Normalize double spaces that may result from replacements
    sanitized_text = "".join(sanitized_chars)
    sanitized_text = re.sub(r' +', ' ', sanitized_text)
    
    return sanitized_text
