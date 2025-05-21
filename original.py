from flask import Flask, request, jsonify, send_from_directory
import json
from groq import Groq
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)  # Allow frontend JS to call backend

# Load knowledge base
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

# Groq API client
client = Groq(api_key="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")  # Replace with your actual key

# Initial message history
messages = [
    {"role": "system", "content": "You are a helpful assistant for Tychi Wallet. Use the context to answer questions accurately."}
]

# Search function
def search_kb(query, kb, max_results=3):
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

# Serve frontend
@app.route('/')
def serve_chat():
    return send_from_directory('static', 'chat.html')

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "")

    kb_matches = search_kb(user_input, knowledge_base)
    context = "\n\n".join(kb_matches) if kb_matches else "No related entries found."

    system_prompt = {
        "role": "system",
        "content": f"You are a Tychi Wallet assistant. Use the following context:\n\n{context}"
    }

    conversation = [system_prompt] + messages[1:]  # Replace system each time
    conversation.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            messages=conversation,
            model="llama3-70b-8192"
        )
        reply = response.choices[0].message.content

        # Save messages
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    import sys
    if sys.argv[0].endswith("debugpy_launcher"):
        app.run(debug=True, use_reloader=False)
    else:
        app.run(debug=True)

