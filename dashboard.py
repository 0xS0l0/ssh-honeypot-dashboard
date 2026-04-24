from flask import Flask, render_template
import json
from collections import Counter, defaultdict
from datetime import datetime
from geoip import get_location

app = Flask(__name__)

LOG_FILE = "logs.json"


def load_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return []


@app.route("/")
def index():
    logs = load_logs()

    # 🌍 Add country info
    for log in logs:
        log["country"] = get_location(log["ip"])

    total_attacks = len(logs)

    ips = [log["ip"] for log in logs]
    passwords = [log["password"] for log in logs]

    top_ips = Counter(ips).most_common(5)
    top_passwords = Counter(passwords).most_common(5)

    # 📊 Attacks per hour
    hourly_attacks = defaultdict(int)

    for log in logs:
        try:
            time = datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            hour = time.strftime("%H:00")
            hourly_attacks[hour] += 1
        except:
            pass

    hours = list(hourly_attacks.keys())
    counts = list(hourly_attacks.values())

    return render_template(
        "index.html",
        total=total_attacks,
        top_ips=top_ips,
        top_passwords=top_passwords,
        logs=logs[::-1],
        hours=hours,
        counts=counts
    )


if __name__ == "__main__":
    app.run(debug=True)
