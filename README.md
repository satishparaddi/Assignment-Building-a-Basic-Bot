# 🤖 Smart Chatbot

This chatbot handles greetings, help, goodbyes, vague inputs, and more using LangChain and OpenAI.

## Features
- Personalized greeting
- Intent detection
- Vague input fallback
- Context-aware response

## Run it locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment
Add your OpenAI key to Streamlit secrets:
```
OPENAI_API_KEY = "your-key"
```