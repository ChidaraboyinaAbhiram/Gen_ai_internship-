import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Fallback to gemini_key if GEMINI_API_KEY is not defined
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('gemini_key')


class GeminiClient:
	"""Lightweight Gemini client using the REST API.

	Reads `GEMINI_API_KEY` (or `gemini_key`) from environment or UI.
	"""

	def __init__(self, api_key: str | None = None, base_url: str | None = None):
		self.api_key = api_key or GEMINI_API_KEY
		self.base_url = base_url or os.getenv('GEMINI_API_URL') or "https://generativelanguage.googleapis.com/v1beta/models"

	def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 1000, model: str = 'gemini-1.5-flash') -> str:
		if not self.api_key:
			raise RuntimeError('GEMINI_API_KEY not set. Add it to your .env file or enter it in the sidebar.')

		# Format model name (ensure it starts without models/ prefix if base_url includes it)
		model_name = model
		if '/' in model_name:
			model_name = model_name.split('/')[-1]

		url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
		
		headers = {
			"Content-Type": "application/json"
		}
		
		payload = {
			"contents": [
				{
					"role": "user",
					"parts": [
						{"text": user_prompt}
					]
				}
			],
			"generationConfig": {
				"temperature": temperature,
				"maxOutputTokens": max_tokens
			}
		}
		
		if system_prompt:
			payload["system_instruction"] = {
				"parts": [
					{"text": system_prompt}
				]
			}
			
		try:
			response = requests.post(url, headers=headers, json=payload, timeout=60)
			response.raise_for_status()
			data = response.json()
			
			if "candidates" in data and len(data["candidates"]) > 0:
				candidate = data["candidates"][0]
				if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
					return candidate["content"]["parts"][0]["text"]
			
			return f"Error: Unexpected response structure from Gemini API: {data}"
		except Exception as e:
			try:
				err_msg = response.text
			except Exception:
				err_msg = ""
			if err_msg:
				return f"Error calling Gemini API: {str(e)} - {err_msg}"
			return f"Error calling Gemini API: {str(e)}"


def generate(system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 1000, model: str = 'gemini-1.5-flash', api_key: str | None = None) -> str:
	"""Convenience function matching the client.generate signature."""
	client = GeminiClient(api_key=api_key)
	return client.generate(system_prompt, user_prompt, temperature=temperature, max_tokens=max_tokens, model=model)

