import json
from collections import defaultdict
from datetime import datetime

LOG_FILE = "logs.json"

def load_logs():
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def detect_bruteforce(logs, threshold=5):
    ip_attempts = defaultdict(int)

    for entry in logs:
        ip_attempts[entry["ip"]] += 1

    print("\n🚨 Brute Force Detection:")
    for ip, count in ip_attempts.items():
        if count >= threshold:
            print(f"[ALERT] {ip} -> {count} attempts")

def detect_suspicious_passwords(logs):
    common_passwords = ["123456", "password", "admin", "root", "toor"]

    print("\n🔑 Weak Password Usage:")
    for entry in logs:
        if entry["password"].lower() in common_passwords:
            print(f"[WEAK] {entry['ip']} used '{entry['password']}'")

def detect_rapid_attempts(logs, time_window=10):
    print("\n⚡ Rapid Attack Detection:")

    ip_times = defaultdict(list)

    for entry in logs:
        ip = entry["ip"]
        time = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
        ip_times[ip].append(time)

    for ip, times in ip_times.items():
        times.sort()

        for i in range(len(times) - 2):
            if (times[i+2] - times[i]).seconds <= time_window:
                print(f"[FAST ATTACK] {ip} made multiple attempts quickly")
                break

if __name__ == "__main__":
    logs = load_logs()

    detect_bruteforce(logs)
    detect_suspicious_passwords(logs)
    detect_rapid_attempts(logs)


