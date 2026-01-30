# 📊 NREGA Reports Collection Tool

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0-green?style=for-the-badge&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue?style=for-the-badge&logo=docker)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

A centralized web application designed to streamline data collection for **NREGA** (National Rural Employment Guarantee Act) operations.  
This tool replaces manual Excel sheets with a structured database system, offering smart suggestions, session memory, and mobile-friendly forms for Block Operators.

---

## 🚀 Key Features

### 1. 📝 Data Entry Modules
The application supports three specific data formats:

- **Semi-Skilled Problems** — Track registration, bank details, and muster roll issues.  
- **Deleted Job Cards** — Log details of deleted job cards with reasons.  
- **Delete Bill/Voucher** — Manage requests for voucher deletion with bill and scheme details.  

---

### 2. 🧠 Smart Features for Operators

- **Session Memory** — Automatically remembers the last entered *Block*, *Panchayat*, and *Village*. No need to retype for consecutive entries.  
- **Auto-Complete Suggestions** — Learns from the database. As you type a location name, it suggests existing Blocks and Panchayats to prevent spelling errors and speed up entry.  

---

### 3. ⚙️ Admin & Management

- **Admin Dashboard** — View all collected data in a clean tabular format.  
- **One-Click Export** — Download data as **CSV** files compatible with Excel.  
- **Data Persistence** — Uses SQLite with Docker volume mapping to ensure data safety.  

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask), SQLAlchemy (ORM)  
- **Frontend:** HTML5, Bootstrap 5 (Mobile Responsive)  
- **Data Handling:** Pandas, OpenPyXL  
- **Deployment:** Docker, Docker Compose, Gunicorn  
- **Server:** Synology NAS (Self-Hosted)  

---

## 💻 Local Installation (For Development)

If you want to run this project on your local machine (Windows/Mac):

### 1. Clone the Repository
```bash
git clone https://github.com/rajatpoddar/Nrega-Reports.git
cd Nrega-Reports
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```

Access the app at:  
👉 http://127.0.0.1:5000

---

## 🐳 Deployment on NAS (Docker)

This project is optimized for deployment on Synology NAS or any Docker-enabled server.

### 1. Initial Setup

Ensure `Dockerfile` and `docker-compose.yml` are present.

```bash
# Build and Run Container
docker-compose up -d --build
```

The application will be accessible at:  
👉 http://<YOUR-NAS-IP>:5233

---

### 2. Data Persistence

The database is mapped to a volume to prevent data loss during restarts:

- **Host Path:** `./data`  
- **Container Path:** `/app/data`  

---

## 🔄 Automatic Updates

To update the application with the latest code from GitHub without manual intervention:

1. SSH into your NAS  
2. Navigate to the project directory  
3. Run the update script:

```bash
./update.sh
```

This script will:

- Pull the latest code  
- Rebuild the Docker container  
- Clean up old images automatically  

---

## 📂 Project Structure

```text
Nrega-Reports/
│
├── app.py                 # Main Flask Application
├── requirements.txt       # Python Dependencies
├── Dockerfile             # Docker Configuration
├── docker-compose.yml     # Container Orchestration
├── update.sh              # Auto-update Script
├── data/                  # Database storage (Persistent)
│   └── nrega_data.db      # SQLite Database
│
└── templates/             # HTML Frontend
    ├── index.html         # Main Menu
    ├── form_semi.html     # Semi-skilled Form
    ├── form_jc.html       # Jobcard Deleted Form
    ├── form_voucher.html  # Voucher Delete Form
    └── admin.html         # Admin Dashboard
```

---

## 👤 Author

**Rajat Poddar**  

- GitHub: `rajatpoddar`

---

© 2025–2026 **NREGA Reports Tool**. All Rights Reserved.
