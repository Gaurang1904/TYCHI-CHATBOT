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

# --- Refined search: short, relevant KB match ---
def search_knowledge_base(user_text):
    user_text_lower = user_text.lower()
    matches = []

    def recursive_search(node):
        if isinstance(node, dict):
            text_fields = []
            if "title" in node:
                text_fields.append(node["title"])
            if "description" in node:
                text_fields.append(node["description"])
            if "example_questions" in node:
                text_fields.extend(node["example_questions"])

            for field in text_fields:
                if isinstance(field, str) and user_text_lower in field.lower():
                    matches.append(node.get("description", field))

            for value in node.values():
                recursive_search(value)

        elif isinstance(node, list):
            for item in node:
                recursive_search(item)

    recursive_search(knowledge_base)

    if matches:
        unique_matches = list(dict.fromkeys(matches))
        return unique_matches  # Return all matches, first is most relevant
    return None

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if "kb_matches" not in st.session_state:
    st.session_state.kb_matches = []

# --- User Input ---
user_input = st.text_input("You:", key="user_input")

if st.button("Send") and user_input:
    user_input_lower = user_input.lower().strip()
    st.session_state.messages.append({"role": "user", "content": user_input})

    # If user wants more info
    if user_input_lower in ["more", "tell me more", "details"]:
        if len(st.session_state.kb_matches) > 1:
            st.session_state.kb_matches.pop(0)  # remove current shown
            reply = st.session_state.kb_matches[0]
        else:
            reply = "That's all I have right now from the knowledge base."
    else:
        kb_matches = search_knowledge_base(user_input)
        if kb_matches:
            st.session_state.kb_matches = kb_matches
            reply = f"{kb_matches[0]}\n\n_(Let me know if you'd like more info!)_"
            st.write("✅ Answered from Knowledge Base")
        else:
            try:
                chat_completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="llama3-70b-8192"
                )
                reply = chat_completion.choices[0].message.content
            except Exception as e:
                reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- Display Chat History ---
for msg in st.session_state.messages[1:]:  # skip system message
    speaker = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{speaker} {msg['role'].capitalize()}**: {msg['content']}")
