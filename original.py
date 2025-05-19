import os
from groq import Groq



# --- Configuration ---
# Store your key securely in production
client = Groq(
    api_key="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",
)

# --- Chat Loop ---
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("🤖 Groq Chatbot is ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Bot: Goodbye!")
        break

    # Add user's message to chat history
    messages.append({"role": "user", "content": user_input})

    try:
        # Get Groq's response
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192"
        )

        # Extract the assistant's reply
        reply = chat_completion.choices[0].message.content
        print("Bot:", reply)

        # Add bot's reply to chat history
        messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        print("Bot: An error occurred:", e)
