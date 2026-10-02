#!/data/data/com.termux/files/usr/bin/bash

echo "======================================"
echo "    JARVIS HINDI AI - AUTO SETUP     "
echo "======================================"

# Update and install dependencies
pkg update -y && pkg upgrade -y
pkg install python git termux-api -y
pip install requests

# Download main script
curl -s -O https://raw.githubusercontent.com/gkpiloveyou96-ai/jarvis-assistant/main/jarvis_hindi.py

echo ""
echo "[✓] Installation complete!"
echo "[!] Apni Gemini API key set karne ke liye chalayein:"
echo "    sed -i 's/YOUR_GEMINI_API_KEY_HERE/APNI_KEY/' jarvis_hindi.py"
echo "[!] JARVIS start karne ke liye chalayein:"
echo "    python jarvis_hindi.py"
echo "======================================"
