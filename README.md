# 🚨 SSH Honeypot with Real-Time SOC Dashboard

A Python-based SSH honeypot that simulates a vulnerable server to capture real-world attack attempts, analyze attacker behavior, and visualize insights through a SOC-style web dashboard.

---

## 📌 Overview

This project mimics a real SSH service to attract and log unauthorized access attempts. It captures attacker IP addresses, credentials, and timestamps, and provides analysis and visualization similar to a **mini Security Operations Center (SOC)** environment.

---

## 📸 Screenshots

> 📌 Add your screenshots inside a `screenshots/` folder

### 🖥️ Dashboard Overview
![Dashboard](screenshots/dashboard-overview.png)

### 📊 Attack Activity (Hourly)
![Chart](screenshots/attack-trends.png)

### 📜 Login Attempts Table
![Logs](screenshots/login-attempts.png)

---

## 🔥 Features

- 🛡️ SSH Honeypot (Paramiko-based fake SSH server)  
- 📊 Real-time attack monitoring dashboard (Flask)  
- 🌍 GeoIP tracking (attacker country identification)  
- 🚨 Brute-force & rapid attack detection  
- 📈 Attack trends visualization (Chart.js)  
- 🔍 Top attacking IPs & most used passwords  
- ⚠️ Threat scoring & risk highlighting  
- 🔄 Auto-refreshing dashboard (live monitoring)  

---


