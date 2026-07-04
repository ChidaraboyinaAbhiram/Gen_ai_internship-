import os
from typing import List, Dict
import google.generativeai as genai
from groq import Groq

# Model configurations
AVAILABLE_MODELS: Dict[str, List[str]] = {
    "Gemini": [
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash"
    ],
    "Groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
}

def get_available_models(provider: str) -> List[str]:
    """
    Returns a list of supported models for a given API provider.
    """
    return AVAILABLE_MODELS.get(provider, [])

def summarize_with_gemini(prompt: str, api_key: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Sends the prompt to Google's Gemini API and returns the generated content.
    
    Args:
        prompt (str): The constructed prompt.
        api_key (str): The Gemini API key.
        model_name (str): The specific Gemini model to use.
        
    Returns:
        str: The LLM response.
    """
    if not api_key:
        raise ValueError("Gemini API Key is missing. Please check your configurations or .env file.")
        
    try:
        genai.configure(api_key=api_key)
        
        # Configure model parameters
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Gemini API returned an empty response. It might be due to safety filters or rate limits.")
            
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
            raise ValueError("The provided Gemini API Key is invalid. Please double-check your key.")
        elif "ResourceExhausted" in error_msg or "429" in error_msg:
            raise ValueError("Gemini API rate limit exceeded. Please wait a moment before trying again.")
        else:
            raise RuntimeError(f"Gemini API Error: {error_msg}")

def summarize_with_groq(prompt: str, api_key: str, model_name: str = "llama-3.3-70b-specdec") -> str:
    """
    Sends the prompt to Groq API and returns the generated content.
    
    Args:
        prompt (str): The constructed prompt.
        api_key (str): The Groq API key.
        model_name (str): The specific Groq model to use.
        
    Returns:
        str: The LLM response.
    """
    if not api_key:
        raise ValueError("Groq API Key is missing. Please check your configurations or .env file.")
        
    try:
        client = Groq(api_key=api_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
            temperature=0.2,
            max_tokens=8192,
            top_p=0.95
        )
        
        content = chat_completion.choices[0].message.content
        
        if not content:
            raise ValueError("Groq API returned an empty response.")
            
        return content
        
    except Exception as e:
        error_msg = str(e)
        if "Unauthorized" in error_msg or "Invalid API Key" in error_msg or "401" in error_msg:
            raise ValueError("The provided Groq API Key is invalid. Please double-check your key.")
        elif "Rate limit" in error_msg or "429" in error_msg:
            raise ValueError("Groq API rate limit exceeded. Please wait a moment before trying again.")
        elif "tokens" in error_msg.lower() or "413" in error_msg or "tpm" in error_msg.lower():
            raise ValueError(
                "The video transcript is too long for the selected Groq model's free-tier token limits.\n\n"
                "💡 **How to solve this in the sidebar:**\n"
                "1. Expand the **🤖 AI Model** section and switch from *llama-3.3-70b-versatile* to **llama-3.1-8b-instant** (which has much higher token rate limits).\n"
                "2. Expand the **⚙️ API Configuration** section and switch to **Gemini** (Gemini's free tier has a 1-million token limit and handles long videos without issues).\n"
                "3. Expand the **📝 Summary Style** section and untick **Include Video Timestamps** to make the transcript shorter."
            )
        else:
            raise RuntimeError(f"Groq API Error: {error_msg}")
