# **Ashveil - README**

## Overview

**Ashveil** is a powerful Windows-based tool designed to demonstrate advanced malware techniques, including **DLL injection**, **memory-based code execution**, and **C2 (Command and Control) server communication**. The tool is focused on providing an educational insight into **rootkit installation** and **stealth operations**. It demonstrates how a backdoor can be installed on a victim machine, how it can stay undetected by common monitoring tools, and how an attacker can control it remotely via a C2 server.

This tool was created to explore the boundaries of evading detection while deploying dangerous payloads. It is crucial to note that this tool is **extremely dangerous** in the wrong hands and can be classified as a **cyber weapon** due to its capabilities. 

> **Disclaimer:** This tool is for **educational purposes only**. Misuse or deployment in unauthorized environments is strictly prohibited. The creator is not responsible for any damage caused by this tool.

## Features

- **Rootkit Installation**: Injects a rootkit into the victim's system to conceal processes and activity from monitoring tools like Task Manager and Windows Explorer.
- **DLL Injection**: Injects shellcode into a target process to install the backdoor without being detected by antivirus or system defenses.
- **Memory-based Execution**: Executes and compiles code directly in system memory without writing to disk, making it harder to detect with traditional signature-based tools.
- **C2 Communication**: Connects to a **Command and Control (C2)** server to allow remote control of the victim machine. Payloads and behavior can be modified via the C2 server.
- **Dynamic Payloads**: The payload can be modified easily in the `server.py` file, allowing flexibility for different attack scenarios.
- **payload selection**: you wil be able to select the payload on startup on the server this will be global for all clients downloading the payload 

## comming features
- **aes encryption**: The payload will be encrypted when sent over the network.
- **new payloads**: new payloads will be coming 
ex. passwords stealer, viewer(live view of pc)
- **easy Installation**: we are creating a new installer so you can infected the victim with only 1 command

## payloads
current payloads in ashveil 
- **SHELL**: a remote to the client if the client is also running the rootkit the shell will have elevated permission.
- **keylogger**: a simple script that will log everything the user types and sends it back to the server and in a .log

## Installation

### Prerequisites

- **Operating System**: Windows
- **Dependencies**: `Flask` (for the C2 server)
    ```bash
    pip install flask
    ```
- **Tools**: You will need Python (preferably Python 3.1) to run the tool before converting it to an executable.

### Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/madmaxvoltro/Ashveil.git
    cd Ashveil
    ```

2. Install dependencies:
    ```bash
    pip install flask
    ```

3. **Running the Tool**:
    - Start the **server**:  
        Run `server/server.py` to set up the attacker’s control environment.
        ```bash
        python server/server.py
        ```

    - Start the **attacker**:  
        Run `attacker/attacker.py` to take controll of the  user with the selected payload.
        ```bash
        python attacker/attacker.py
        ```

4. **Injection Process**:
    - The tool will be downloaded in the roaming folder.
    - The rootkit is installed into system memory, with no files written to disk.
    - After installation, the victim system connects back to the attacker's C2 server, allowing for remote control.

## Configuration

### Modifying the Payload

The payload and its behavior can be easily modified by editing the the payloads in ``server/payloads/`` here you can create new payloads who will be auto implemented into the selection menu or you can modifying the existing payloads

1. open ``server/payload/``
2. create a new cs file and implement your code
3. restart the server

> payloads can only be in c#

### Customizing the C2 Server

You can change the behavior of the C2 server will be asked at startup but you can also change the communication parts for example the port

```python
# Example: Set custom port for the C2 server
port = 7777 # Change this to your desired port
```

## Safety Warning

**Ashveil** is a **highly dangerous tool** that can be used as a cyber weapon. It has the potential to cause significant damage if misused. This tool is only intended for **educational purposes** and should be used **ONLY in controlled environments** such as virtual machines or isolated networks.

- **Level of Danger**: This tool is rated **95/100** on the scale of danger this can be seen as a cyber weapon.
- **Important**: It is **your responsibility** to ensure this tool is not used for malicious purposes. The creator will not be held liable for any damages or illegal actions taken using this tool.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Ethics & Responsible Use

Ashveil is designed solely for educational purposes, ethical red teaming, and malware research training in controlled, consent-based environments. It must never be used on real systems without explicit permission.

By using this tool, you agree to abide by all applicable laws and responsible disclosure practices.

## Acknowledgments

- **Rootkit Code**: The rootkit used in this project was **not created by the author** but was sourced from another project. Credits go to the original creator for the rootkit code byte77.
  
## Contact

If you have any questions or need further assistance, feel free to reach out.
