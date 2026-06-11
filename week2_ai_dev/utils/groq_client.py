# utils/groq_client.py
import groq
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_groq_client(api_key=None):
	return groq.Groq(api_key=api_key or os.getenv('GROQ_API_KEY'))

def generate(system_prompt, user_prompt, temperature=0.7, max_tokens=1000, model='llama-3.3-70b-versatile', api_key=None):
	client = get_groq_client(api_key)
	try:
		response = client.chat.completions.create(
			model=model,
			messages=[
				{'role': 'system', 'content': system_prompt},
				{'role': 'user', 'content': user_prompt}
			],
			temperature=temperature,
			max_tokens=max_tokens
		)
		return response.choices[0].message.content
	except Exception as e:
		return f'Error: {str(e)}'

def translate_content(text, target_language, model='llama-3.3-70b-versatile', api_key=None):
	system_prompt = f'You are an expert translator. Translate to {target_language}. Return ONLY the translation.'
	return generate(system_prompt, text, temperature=0.1, max_tokens=1000, model=model, api_key=api_key)