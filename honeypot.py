import socket
import threading
import paramiko
import datetime
import json
import os
import uuid
import time

HOST = "0.0.0.0"
PORT = 2222
LOG_FILE = "logs.json"

lock = threading.Lock()

host_key = paramiko.RSAKey.generate(2048)

WEAK_CREDS = {
    "root": ["root", "toor", "123456", "password"],
    "admin": ["admin", "123456", "password"],
    "user": ["user", "password"]
}


# ---------------- LOGGING ---------------- #

def log_attempt(ip, username, password, success):
    session_id = str(uuid.uuid4())

    data = {
        "session_id": session_id,
        "timestamp": str(datetime.datetime.now()),
        "ip": ip,
        "username": username,
        "password": password,
        "success": success,
        "commands": []
    }

    with lock:
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
            else:
                logs = []
        except:
            logs = []

        logs.append(data)

        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)

    return session_id


def log_command(session_id, command):
    with lock:
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except:
            return

        for entry in logs:
            if entry["session_id"] == session_id:
                entry["commands"].append({
                    "command": command,
                    "time": str(datetime.datetime.now())
                })

        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)


# ---------------- SSH HANDLER ---------------- #

class SSHHandler(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.session_id = None
        self.authenticated = False

    def check_auth_password(self, username, password):
        time.sleep(0.8)  # slow brute force

        success = username in WEAK_CREDS and password in WEAK_CREDS[username]

        self.session_id = log_attempt(self.client_ip, username, password, success)

        if success:
            self.authenticated = True
            print(f"[+] SUCCESS {username}:{password}")
            return paramiko.AUTH_SUCCESSFUL
        else:
            print(f"[-] FAIL {username}:{password}")
            return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_pty_request(self, channel, *args):
        return True


# ---------------- SHELL ---------------- #

def fake_shell(channel, session_id):
    try:
        channel.send("Ubuntu 20.04 LTS\r\n")
        channel.send("root@server:~# ")

        buffer = ""

        while True:
            data = channel.recv(1024)
            if not data:
                break

            # Echo input so user sees typing
            channel.send(data)

            buffer += data.decode("utf-8", errors="ignore")

            # Wait until Enter
            if "\n" not in buffer and "\r" not in buffer:
                continue

            command = buffer.replace("\r", "").replace("\n", "").strip()
            buffer = ""

            if not command:
                channel.send("root@server:~# ")
                continue

            print(f"[CMD] {command}")
            log_command(session_id, command)

            if command.lower() in ["exit", "quit"]:
                channel.send("\r\nlogout\r\n")
                break

            elif command == "whoami":
                channel.send("\r\nroot\r\n")

            elif command == "ls":
                channel.send("\r\nfile1.txt  secrets.txt  backup.zip\r\n")

            elif command == "pwd":
                channel.send("\r\n/root\r\n")

            else:
                channel.send(f"\r\n{command}: command not found\r\n")

            channel.send("root@server:~# ")

    except Exception as e:
        print(f"Shell error: {e}")

    finally:
        channel.close()


# ---------------- CLIENT HANDLER ---------------- #

def handle_client(client, addr):
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)

        server = SSHHandler(addr[0])

        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            return

        # Allow time for auth attempts (important for tools)
        channel = transport.accept(60)

        if channel is None:
            return

        if server.authenticated:
            fake_shell(channel, server.session_id)
        else:
            # Don't instantly drop → helps stability
            time.sleep(2)
            channel.close()

    except Exception as e:
        print(f"Connection error: {e}")

    finally:
        try:
            transport.close()
        except:
            pass
        client.close()


# ---------------- SERVER ---------------- #

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(200)

    print(f"[+] Honeypot running on port {PORT}")

    while True:
        client, addr = sock.accept()
        print(f"[+] Connection from {addr[0]}")

        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    start_server()
