import streamlit as st
from groq import Groq

# --- Initialize Groq Client ---
client = Groq(
    api_key="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"
)

st.set_page_config(page_title="Groq Chatbot")
st.title("🤖 Groq Chatbot")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# --- User Input ---
user_input = st.text_input("You:", key="user_input")

if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Get response from Groq API
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama3-70b-8192"
        )
        reply = chat_completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        reply = f"Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": reply})

# --- Display Conversation ---
for msg in st.session_state.messages[1:]:  # skip system message
    speaker = "🧑" if msg["role"] == "user" else "🤖"
    st.markdown(f"**{speaker} {msg['role'].capitalize()}**: {msg['content']}")

