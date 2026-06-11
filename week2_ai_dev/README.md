# Capstone Project — AI Writing Assistant

This is a Streamlit-based AI Writing Assistant (Capstone project).

## Setup

1. Create a Python virtual environment and activate it.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or cmd
.\.venv\Scripts\activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your API keys:

```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the app

```bash
streamlit run ai_writing_assistant.py
```

## Notes
- The project reads API keys from environment variables using `python-dotenv`.
- `utils/groq_client.py` already reads `GROQ_API_KEY` from the environment.
- `utils/gemini_client.py` is a lightweight wrapper that reads `GEMINI_API_KEY` from the environment and provides a placeholder `generate` method — replace the stub with actual API integration if needed.
