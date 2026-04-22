# 🔐 Flask + MySQL Auth System

A full-stack login & signup system built with Python Flask and MySQL.

## 📁 Project Structure

```
auth_app/
├── app.py               ← Flask app (routes, DB logic, password hashing)
├── requirements.txt     ← Python packages needed
├── Dockerfile           ← Docker image definition
├── docker-compose.yml   ← Multi-container setup (app + MySQL)
├── setup.sql            ← Optional: run manually in MySQL to create DB
└── templates/
    ├── base.html        ← Shared layout
    ├── index.html       ← Landing page
    ├── signup.html      ← Sign-up form
    ├── login.html       ← Login form
    └── dashboard.html   ← Protected dashboard
```

---

## ⚡ Quick Start (Local — no Docker)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure via Environment Variables
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_mysql_password
export DB_NAME=auth_db
export SECRET_KEY=some-random-secret
```

Or create a `.env` file and load it before running.

### 3. Run
```bash
python app.py
```
> ✅ The app automatically creates `auth_db` database and `users` table on first run.

### 4. Open Browser
```
http://localhost:5000
```

---

## 🐳 Docker Quick Start

```bash
docker-compose up --build
```

The app will be available at `http://localhost:5000`.

> The app service waits for MySQL to pass its healthcheck before starting,
> so no manual delays or retries are needed.

### Changing the secret key (recommended)
Edit `docker-compose.yml` and replace the `SECRET_KEY` value:
```yaml
- SECRET_KEY=replace-with-a-strong-random-secret
```

---

## 🔄 Flow
1. **Sign Up** → Enter name + email/mobile + password → stored in MySQL with bcrypt hash
2. **Log In** → Enter same email/mobile + password → session created
3. **Dashboard** → Protected page, only accessible when logged in
4. **Log Out** → Session cleared

---

## 🛠 Tech Stack
| Layer       | Tech                      |
|-------------|---------------------------|
| Backend     | Python 3 + Flask          |
| Database    | MySQL via mysql-connector |
| Auth        | bcrypt password hashing   |
| Sessions    | Flask server-side session |
| Frontend    | HTML/CSS/JS (no framework)|
| Container   | Docker + docker-compose   |
