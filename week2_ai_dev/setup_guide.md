# AI Writing Assistant Setup Guide

This guide explains how to set up the environment, configure the environment variables, and run the Streamlit application.

---

## 1. Setting Up the Virtual Environment

Creating a virtual environment ensures that the dependencies for this project do not conflict with other Python projects on your system.

### On Windows (PowerShell)
```powershell
# Create a virtual environment named '.venv'
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

### On Windows (CMD)
```cmd
# Create a virtual environment named '.venv'
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\activate.bat
```

### On macOS / Linux
```bash
# Create a virtual environment named '.venv'
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

---

## 2. Installing Dependencies

Once the virtual environment is activated, run this command to install the required libraries (`streamlit`, `groq`, `requests`, and `python-dotenv`):

```bash
pip install -r requirements.txt
```

---

## 3. Configuring Environment Variables (.env)

The application looks for your API keys in a file named `.env` in the root of the project directory.

1. Create a file named `.env` (you can copy `.env.example`).
2. Add your API keys:

```env
# Your Groq API Key (starts with gsk_)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Your Gemini API Key (starts with AIzaSy)
GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here
```

> [!NOTE]
> If you do not have these keys configured in your `.env` file, you can also paste them directly in the **Model Configuration** panel in the sidebar of the app while it is running.

---

## 4. How to Run the Application

Start the Streamlit web server by running:

```bash
streamlit run ai_writing_assistant.py
```

Streamlit will launch a local server and output the access URL (usually **http://localhost:8501**). Open this link in your browser to start using the writing assistant.
