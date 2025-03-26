# Remote Administration Toolkit (RAT)

## Overview
- This is a remote administration toolkit that consists of both a server and a client. 
- The server acts as a control panel for managing multiple connected clients, while the client establishes a persistent connection to the server, allowing for remote command execution.

⚠️ Disclaimer: This tool is strictly for educational and ethical use only. Unauthorized use on systems without explicit permission is illegal and violates cybersecurity laws.

## Features
```
	>  Multi-Client Management – Handles multiple clients simultaneously.
	>  Remote Command Execution – Send commands from the server and execute them on clients.
	>  Heartbeat Monitoring – Keeps track of connected clients and removes inactive ones.
	>  Auto-Reconnect – Ensures stable connections with retry mechanisms.
	>  Persistence (Client Side) – The client can automatically re-launch on startup.
	> Cross-Platform – Works on Windows, Linux, and macOS.
```

## Requirements
- Python 3.x
- Colorama

## Server (Control Panel) Setup
The server listens for incoming connections from clients.

### **Server Commands**  

| Command        | Description                                  |
|--------------|----------------------------------|
| `list`       | Show active clients.                     |
| `select <id>` | Interact with a specific client.        |
| `clear`      | Clear the screen.                        |
| `quit`       | Shut down the server.                    |


## Client Setup
The client is deployed on the target machine and connects to the server automatically.

- Configure the Client
Modify the ``host`` and ``port`` variables inside client.py

## Security Warning
This tool must not be used for unauthorized access or malicious activities. 

Using it on systems without explicit permission is illegal and can result in severe penalties. 

Always obtain explicit consent before deploying.
