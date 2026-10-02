from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# Yahan apni actual Gemini API key daalein
GEMINI_API_KEY = "AQ.Ab8RN6KU8ipIU1J3EWzadLJULhQqOHlAlOAF5ykLZ1MiNFjZFQ"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Online</title>
    <style>
        body { background: #0A0E17; color: #00E5FF; font-family: sans-serif; text-align: center; padding: 20px; }
        h1 { font-size: 28px; letter-spacing: 2px; }
        #box { width: 90%; max-width: 400px; padding: 12px; border-radius: 8px; border: 1px solid #00E5FF; background: #111; color: white; font-size: 16px; }
        button { margin-top: 15px; padding: 12px 24px; background: #00E5FF; border: none; font-weight: bold; font-size: 16px; border-radius: 8px; cursor: pointer; }
        #response { margin-top: 25px; font-size: 18px; color: #fff; line-height: 1.5; }
    </style>
</head>
<body>
    <h1>J.A.R.V.I.S.</h1>
    <p>Voice & Text AI Web Console</p>
    <input type="text" id="box" placeholder="Ask Jarvis anything..." />
    <br>
    <button onclick="askJarvis()">Send Command</button>
    <div id="response">Waiting for query...</div>

    <script>
        async function askJarvis() {
            let query = document.getElementById("box").value;
            if(!query) return;
            document.getElementById("response").innerText = "Thinking...";
            let res = await fetch("/ask?query=" + encodeURIComponent(query));
            let data = await res.json();
            document.getElementById("response").innerText = data.reply;
            
            let speech = new SpeechSynthesisUtterance(data.reply);
            window.speechSynthesis.speak(speech);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/ask')
def ask():
    user_query = request.args.get("query", "")
    if not user_query:
        return jsonify({"reply": "Sir, I did not receive any command."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": f"You are JARVIS. Answer concisely in 1 to 2 spoken sentences: {user_query}"}]
        }]
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        reply = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return jsonify({"reply": reply})
    except Exception:
        return jsonify({"reply": "Unable to connect to central servers."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
