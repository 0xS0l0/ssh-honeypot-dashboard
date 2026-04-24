import json
from collections import Counter

with open("logs.json") as f:
    logs = json.load(f)

ips = [entry["ip"] for entry in logs]
passwords = [entry["password"] for entry in logs]

print("\nTop Attacking IPs:")
for ip, count in Counter(ips).most_common(5):
    print(f"{ip} -> {count} attempts")

print("\nMost Used Passwords:")
for pwd, count in Counter(passwords).most_common(5):
    print(f"{pwd} -> {count} times")
