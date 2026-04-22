from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
import bcrypt
import re
import os

app = Flask(__name__)
# FIX: Use a stable secret key from env so sessions survive restarts.
# In production, always set SECRET_KEY as a strong random env variable.
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')

# ─── Database Configuration ───────────────────────────────────────────────────
# FIX: Read all credentials from environment variables instead of hardcoding.
# This makes the app work both locally and inside Docker without code changes.
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'user':     os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'auth_db')
}

def get_db_connection():
    """Create and return a MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None

def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                full_name   VARCHAR(100)         NOT NULL,
                email       VARCHAR(100)         UNIQUE,
                mobile      VARCHAR(15)          UNIQUE,
                password    VARCHAR(255)         NOT NULL,
                created_at  TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT chk_identifier CHECK (email IS NOT NULL OR mobile IS NOT NULL)
            )
        """)
        conn.commit()
        print("[DB] Database and tables initialised successfully.")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[DB INIT ERROR] {e}")

# ─── Helpers ──────────────────────────────────────────────────────────────────
def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email)

def is_valid_mobile(mobile):
    return re.match(r'^\+?\d{10,15}$', mobile)

def hash_password(plain_text):
    return bcrypt.hashpw(plain_text.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(plain_text, hashed):
    return bcrypt.checkpw(plain_text.encode('utf-8'), hashed.encode('utf-8'))

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name   = request.form.get('full_name', '').strip()
        identifier  = request.form.get('identifier', '').strip()
        password    = request.form.get('password', '')
        confirm_pw  = request.form.get('confirm_password', '')

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not identifier:
            errors.append("Email or mobile number is required.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_pw:
            errors.append("Passwords do not match.")

        email  = None
        mobile = None
        if identifier:
            if '@' in identifier:
                if not is_valid_email(identifier):
                    errors.append("Invalid email address.")
                else:
                    email = identifier
            else:
                if not is_valid_mobile(identifier):
                    errors.append("Invalid mobile number (10–15 digits).")
                else:
                    mobile = identifier

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('signup.html', form_data=request.form)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Please try again.", 'error')
            return render_template('signup.html', form_data=request.form)

        cursor = conn.cursor(dictionary=True)
        try:
            if email:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            else:
                cursor.execute("SELECT id FROM users WHERE mobile = %s", (mobile,))

            if cursor.fetchone():
                flash("An account with this email/mobile already exists.", 'error')
                return render_template('signup.html', form_data=request.form)

            hashed_pw = hash_password(password)
            cursor.execute(
                "INSERT INTO users (full_name, email, mobile, password) VALUES (%s, %s, %s, %s)",
                (full_name, email, mobile, hashed_pw)
            )
            conn.commit()
            flash("Account created successfully! Please log in.", 'success')
            return redirect(url_for('login'))

        except Error as e:
            conn.rollback()
            flash(f"Database error: {e}", 'error')
            return render_template('signup.html', form_data=request.form)
        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html', form_data={})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '')

        if not identifier or not password:
            flash("All fields are required.", 'error')
            return render_template('login.html')

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Please try again.", 'error')
            return render_template('login.html')

        cursor = conn.cursor(dictionary=True)
        try:
            if '@' in identifier:
                cursor.execute("SELECT * FROM users WHERE email = %s", (identifier,))
            else:
                cursor.execute("SELECT * FROM users WHERE mobile = %s", (identifier,))

            user = cursor.fetchone()

            if not user or not check_password(password, user['password']):
                flash("Invalid credentials. Please try again.", 'error')
                return render_template('login.html')

            session['user_id']    = user['id']
            session['user_name']  = user['full_name']
            session['user_email'] = user['email'] or user['mobile']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            return redirect(url_for('dashboard'))

        except Error as e:
            flash(f"Database error: {e}", 'error')
            return render_template('login.html')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.", 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html',
                           name=session['user_name'],
                           email=session['user_email'])


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", 'success')
    return redirect(url_for('index'))


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
