import socket
import threading
import paramiko
import datetime
import json

HOST = "0.0.0.0"
PORT = 2222  # safer than 22

LOG_FILE = "logs.json"

# Generate fake SSH host key
host_key = paramiko.RSAKey.generate(2048)

def log_attempt(ip, username, password):
    data = {
        "timestamp": str(datetime.datetime.now()),
        "ip": ip,
        "username": username,
        "password": password
    }

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(data)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

    print(f"[+] Login attempt from {ip} | {username}:{password}")
    
    # simple alert
    if password.lower() in ["admin", "123456", "password"]:
        print(f"[ALERT] Weak password attempt from {ip}")

class SSHHandler(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip

    def check_auth_password(self, username, password):
        log_attempt(self.client_ip, username, password)
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def handle_client(client, addr):
    transport = paramiko.Transport(client)
    transport.add_server_key(host_key)

    server = SSHHandler(addr[0])

    try:
        transport.start_server(server=server)
        channel = transport.accept(20)

        if channel is not None:
            channel.close()

    except Exception as e:
        print(f"[-] Error: {e}")

    finally:
        transport.close()
        client.close()

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(100)

    print(f"[+] Honeypot running on port {PORT}...")

    while True:
        client, addr = sock.accept()
        print(f"[+] Connection from {addr[0]}")

        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
