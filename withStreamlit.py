import streamlit as st
import json
from groq import Groq

# --- Initialize Groq Client ---
client = Groq(
    api_key="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"
)

st.set_page_config(page_title="Groq Chatbot")
st.title("🤖 Groq Chatbot")

# --- Load Knowledge Base JSON ---
@st.cache_data
def load_knowledge_base():
    with open("knowledge_base.json", "r") as f:
        return json.load(f)

knowledge_base = load_knowledge_base()

# --- Simple function to search knowledge base ---
def search_knowledge_base(user_text):
    # naive search: check if any key or section description contains user input keywords
    user_text_lower = user_text.lower()
    answers = []

    def recursive_search(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (str, list)):
                    # Check keys and string values
                    if isinstance(v, str) and user_text_lower in v.lower():
                        answers.append(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, str) and user_text_lower in item.lower():
                                answers.append(item)
                elif isinstance(v, dict):
                    recursive_search(v)

        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item)

    recursive_search(knowledge_base)

    if answers:
        # Return the first few matched answers joined
        return "\n\n".join(answers[:3])
    else:
        return None

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# --- User Input ---
user_input = st.text_input("You:", key="user_input")

if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Try to fetch answer from knowledge base first
    kb_reply = search_knowledge_base(user_input)

    if kb_reply:
        reply = kb_reply
    else:
        try:
            # Get response from Groq API
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama3-70b-8192"
            )
            reply = chat_completion.choices[0].message.content
        except Exception as e:
            reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- Display Conversation ---
for msg in st.session_state.messages[1:]:  # skip system message
    speaker = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{speaker} {msg['role'].capitalize()}**: {msg['content']}")
