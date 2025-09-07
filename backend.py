# backend.py
# This script is the server 'brain' for your chatbot website.

from flask import Flask, request, jsonify, render_template
import requests
import json
import time

# Initialize the Flask web application
app = Flask(__name__)

# --- Gemini API Function (The same one you tested) ---
def generate_bot_response(user_input):
    """
    Calls the Gemini API to get a response for the user's input.
    """
    system_prompt = """You are a friendly and professional chatbot for a credit card fraud detection website. Your purpose is to assist users by answering their questions about credit card fraud, security best practices, and how to use the website's features.

    Your core responsibilities are:
    1.  **Educate on Fraud:** Explain common types of credit card fraud (e.g., skimming, phishing, identity theft) in simple terms.
    2.  **Provide Security Tips:** Offer actionable advice on how users can protect themselves (e.g., strong passwords, checking statements, being wary of suspicious links).
    3.  **Guide Website Usage:** Help users navigate the website, understand their dashboard, and interpret fraud alerts.
    4.  **Handle Suspected Fraud:** Instruct users on the immediate steps to take if they suspect fraud (e.g., contact their bank, freeze their card).
    5.  **Stay On-Topic:** Politely decline to answer questions that are not related to credit card fraud, finance, or website features. You can say something like, "I can only help with questions related to credit card fraud and security. How can I assist you with that?"

    Keep your answers concise, clear, and helpful."""

    # --- IMPORTANT ---
    # Paste your API key here, just like you did for the terminal test.
    api_key = "AIzaSyD7ftonHFr7EcXj_X9HkzlFg2qM2_GdMus"
    # -----------------

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": user_input}]}],
        "systemInstruction": { "parts": [{"text": system_prompt}] },
    }
    
    headers = {'Content-Type': 'application/json'}
    max_retries = 3
    delay = 1

    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()
            
            result = response.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
            
            if text:
                return text
            else:
                return "I'm sorry, I couldn't generate a valid response. Please try again."

        except requests.exceptions.RequestException as e:
            print(f"API request failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return "There was an error connecting to the service. Please try again."
    
    return "I'm sorry, I couldn't get a response after several attempts."


# --- Flask Web Routes ---
@app.route('/')
def home():
    """This route serves your frontend.html file to the browser."""
    return render_template('frontend.html')

@app.route('/chat', methods=['POST'])
def chat():
    """This route receives messages from the frontend, gets a bot reply, and sends it back."""
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    bot_reply = generate_bot_response(user_message)
    return jsonify({"reply": bot_reply})

# This line starts the web server when you run the script
if __name__ == '__main__':
    app.run(debug=True)

