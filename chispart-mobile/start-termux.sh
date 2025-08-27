#!/bin/bash
echo "🚀 Starting Chispart Mobile for Termux..."

# Ensure termux-wake-lock is held to prevent the app from sleeping
termux-wake-lock

echo "✅ Wake lock acquired. The app will keep running in the background."
echo "🌐 Access it from this device at http://localhost:5000"
echo "   or from other devices on the same network via this device's IP address."

python app.py --host 0.0.0.0 --port 5000

termux-wake-unlock