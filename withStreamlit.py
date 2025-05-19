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

# --- Improved search function for KB ---
def search_knowledge_base(user_text):
    user_keywords = user_text.lower().split()
    results = []

    def recursive_search(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "example_questions" and isinstance(value, list):
                    for question in value:
                        question_lower = question.lower()
                        # Check if any user keyword is in this question
                        if any(keyword in question_lower for keyword in user_keywords):
                            if "description" in node:
                                results.append(node["description"])
                            return True
                elif isinstance(value, (dict, list)):
                    found = recursive_search(value)
                    if found:
                        if "description" in node:
                            results.append(node["description"])
                        return True
        elif isinstance(node, list):
            for item in node:
                found = recursive_search(item)
                if found:
                    return True
        return False

    recursive_search(knowledge_base)
    if results:
        unique_results = list(dict.fromkeys(results))
        return "\n\n".join(unique_results)
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
