import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from fuzzywuzzy import fuzz

# Initialize session state variables
for key, default in {
    'messages': [],
    'user_name': None,
    'user_email': None,
    'awaiting_help_response': False,
    'new_user_input': ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Intent classification
INTENTS = {
    "greeting": ["hello", "hi", "hey", "greetings"],
    "help": ["help", "assist", "support", "question"],
    "goodbye": ["bye", "goodbye", "see you", "farewell"],
    "thanks": ["thanks", "thank you"]
}
VAGUE_RESPONSES = ["maybe", "not sure", "i don't know", "whatever", "any", "something", "idk"]

def classify_intent(user_input):
    user_input = user_input.lower()
    for intent, keywords in INTENTS.items():
        if any(keyword in user_input for keyword in keywords):
            return intent
    return "unknown"

def is_vague_input(user_input):
    return any(fuzz.partial_ratio(user_input.lower(), phrase) > 80 for phrase in VAGUE_RESPONSES)

# System prompt
SYSTEM_PROMPT = """
You are a professional, friendly, and highly intelligent chatbot. Your goals are:
- Provide a warm welcome to every user and introduce yourself.
- Recognize user intents such as greetings, requests for help, and farewells.
- Encourage users to phrase statements as questions when necessary.
- Handle vague inputs with polite clarifications.
- Always respond concisely and informatively while maintaining a natural conversational flow.
- End conversations politely and ensure a smooth transition out.
- Gracefully handle errors and fallback cases.
"""

# Page setup
st.set_page_config(page_title="Smart Chatbot", layout="centered")
st.title("🤖 Smart Chatbot")

# User details
user_name = st.text_input("Please enter your name", value=st.session_state.user_name or "")
user_email = st.text_input("Please enter your email", value=st.session_state.user_email or "")
if user_name:
    st.session_state.user_name = user_name
if user_email:
    st.session_state.user_email = user_email

if st.session_state.user_name:
    st.write(f"Hello, {st.session_state.user_name}! How can I assist you today?")
else:
    st.write("Hello! I'm your friendly AI assistant. How can I help you today?")

# Initialize chat model
chat_model = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=st.secrets["OPENAI_API_KEY"]
)

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Controlled input box
with st.form("chat_input_form", clear_on_submit=True):
    user_input = st.text_input("Your message:", value="")
    submitted = st.form_submit_button("Send")
    if submitted and user_input:
        st.session_state.new_user_input = user_input

# Message processing (only once)
if st.session_state.new_user_input:
    user_input = st.session_state.new_user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    intent = classify_intent(user_input)

    if st.session_state.awaiting_help_response:
        response = user_input.lower()
        if response in ["yes", "yeah", "yep"]:
            bot_response = "Please specify what you need help with."
        elif response in ["no", "nah", "nope"]:
            bot_response = "Alright, feel free to reach out if you have more questions!"
        else:
            bot_response = "Hmm, I didn’t quite catch that. Could you please clarify?"
        st.session_state.awaiting_help_response = False

    elif intent == "greeting":
        bot_response = "👋 Hi there! How can I assist you today?"

    elif intent == "help":
        bot_response = "I'm here to help! Do you need assistance with something specific?"
        st.session_state.awaiting_help_response = True

    elif intent == "goodbye":
        bot_response = "👋 Goodbye! Have a great day!"

    elif intent == "thanks":
        bot_response = "You're welcome! Let me know if there's anything else."

    elif is_vague_input(user_input):
        bot_response = "🤷 I'm sorry, I didn't quite understand. Could you please clarify?"

    else:
        context = "\n".join([msg["content"] for msg in st.session_state.messages[-5:]])
        response = chat_model([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"{context}\nUser: {user_input}")
        ])
        bot_response = response.content

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.session_state.new_user_input = ""

# Footer
st.markdown("---")
st.caption("🤖 Powered by OpenAI & Streamlit")