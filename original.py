import os
import json
from groq import Groq

# --- Load Knowledge Base ---
with open('knowledge_base.json.json', 'r') as f:
    knowledge_base = json.load(f)

# --- Groq Client Setup ---
client = Groq(
    api_key="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",
)

# --- Chat History ---
messages = [
    {"role": "system", "content": "You are a helpful assistant for Tychi Wallet. Use the context to answer questions accurately."}
]

# --- Function to Search Knowledge Base ---
def search_knowledge_base(query, kb, max_results=3):
    results = []
    query = query.lower()
    for category in kb.get("categories", []):
        for entry in category.get("entries", []):
            title = entry.get("title", "").lower()
            content = entry.get("content", "").lower()
            if query in title or query in content:
                results.append(f"{entry['title']}: {entry['content']}")
            if len(results) >= max_results:
                return results
    return results

# --- Main Loop ---
print("🤖 Tychi Chatbot is ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Bot: Goodbye!")
        break

    # Search relevant info from KB
    kb_matches = search_knowledge_base(user_input, knowledge_base)

    # Build context prompt
    context_text = "\n\n".join(kb_matches) if kb_matches else "No related entries found in the knowledge base."

    # Add system prompt with context
    system_prompt = {
        "role": "system",
        "content": f"You are a Tychi Wallet assistant. Use the following context to answer the user:\n\n{context_text}"
    }

    # Update message list (override system prompt for each turn with new context)
    conversation = [system_prompt] + messages[1:]  # Preserve user-assistant history, but replace system

    # Add current user message
    conversation.append({"role": "user", "content": user_input})

    try:
        # Get Groq's response
        chat_completion = client.chat.completions.create(
            messages=conversation,
            model="llama3-70b-8192"
        )

        reply = chat_completion.choices[0].message.content
        print("Bot:", reply)

        # Update message history
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        print("Bot: An error occurred:", e)
