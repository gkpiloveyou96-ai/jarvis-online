from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# Apni Gemini API Key yahan daalein
GEMINI_API_KEY = "AQ.Ab8RN6Lzc6nE1VvT9LoER7q3SMTkDZ1jRequwpe1jwfppD2Jrg"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Voice Console</title>
    <style>
        body { 
            background: #0A0E17; 
            color: #00E5FF; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; 
            padding: 30px 15px;
            margin: 0;
        }
        h1 { font-size: 32px; letter-spacing: 3px; margin-bottom: 5px; }
        p { color: #88a0b0; font-size: 14px; margin-top: 0; }
        
        .mic-btn {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: #00E5FF;
            border: none;
            font-size: 36px;
            cursor: pointer;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.4);
            margin: 30px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, background 0.2s;
        }
        .mic-btn:active { transform: scale(0.95); }
        .listening { 
            background: #ff3366 !important; 
            box-shadow: 0 0 35px rgba(255, 51, 102, 0.7) !important;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.08); }
            100% { transform: scale(1); }
        }

        #status { font-size: 16px; color: #00E5FF; margin-bottom: 20px; font-weight: bold; }
        #query { font-size: 18px; color: #fff; margin: 15px 0; min-height: 25px; }
        #response { 
            font-size: 20px; 
            color: #e0f7fa; 
            line-height: 1.6; 
            background: #111a28; 
            padding: 20px; 
            border-radius: 12px;
            border: 1px solid #1a3048;
            max-width: 500px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <h1>J.A.R.V.I.S.</h1>
    <p>ONLINE VOICE INTELLIGENCE</p>

    <button id="micBtn" class="mic-btn" onclick="toggleListening()">🎤</button>
    <div id="status">Tap Mic to Speak</div>
    <div id="query"></div>
    <div id="response">Awaiting command, Sir...</div>

    <script>
        const micBtn = document.getElementById('micBtn');
        const statusText = document.getElementById('status');
        const queryText = document.getElementById('query');
        const responseText = document.getElementById('response');

        // Browser Speech Recognition setup
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let isListening = false;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-IN'; // English & Hindi mixed friendly

            recognition.onstart = () => {
                isListening = true;
                micBtn.classList.add('listening');
                statusText.innerText = "Listening... (Boliye)";
            };

            recognition.onresult = (event) => {
                const spokenText = event.results[0][0].transcript;
                queryText.innerText = 'You: "' + spokenText + '"';
                sendToJarvis(spokenText);
            };

            recognition.onerror = (event) => {
                statusText.innerText = "Mic error: " + event.error;
                stopListening();
            };

            recognition.onend = () => {
                stopListening();
            };
        } else {
            statusText.innerText = "Speech recognition not supported in this browser. Use Chrome.";
        }

        function toggleListening() {
            if (!recognition) return;
            if (isListening) {
                recognition.stop();
            } else {
                window.speechSynthesis.cancel(); // Stop talking if previously speaking
                recognition.start();
            }
        }

        function stopListening() {
            isListening = false;
            micBtn.classList.remove('listening');
            statusText.innerText = "Tap Mic to Speak";
        }

        async function sendToJarvis(query) {
            statusText.innerText = "Thinking...";
            responseText.innerText = "Processing mainframe request...";

            try {
                let res = await fetch("/ask?query=" + encodeURIComponent(query));
                let data = await res.json();
                
                responseText.innerText = data.reply;
                statusText.innerText = "Ready";

                // Speak out the reply using Android/Browser SpeechSynthesis
                let utterance = new SpeechSynthesisUtterance(data.reply);
                utterance.pitch = 1.0;
                utterance.rate = 1.0;
                window.speechSynthesis.speak(utterance);

            } catch (err) {
                responseText.innerText = "Error contacting Jarvis mainframe.";
                statusText.innerText = "Error";
            }
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
            "parts": [{"text": f"You are JARVIS. Answer concisely in 1 to 2 spoken sentences without markdown formatting: {user_query}"}]
        }]
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        reply = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return jsonify({"reply": reply})
    except Exception:
        return jsonify({"reply": "Network server unreachable."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
