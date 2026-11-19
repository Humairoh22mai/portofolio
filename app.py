
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Kunci session untuk pengembangan
app.secret_key = "ganti-dengan-kunci-rahasia-kamu"

# Akun admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")


# Memeriksa apakah admin sudah login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


app = Flask(__name__)

# Menghubungkan program dengan database SQLite
DATABASE = "database.db"


# Fungsi untuk menghubungkan database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Membuat tabel proyek jika belum tersedia
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            deskripsi TEXT NOT NULL,
            teknologi TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Halaman utama
@app.route("/")
def index():
    conn = get_db_connection()

    data_proyek = conn.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        projects=data_proyek
    )


# Halaman tentang saya
@app.route("/about")
def about():
    return render_template("about.html")


# Menampilkan semua proyek
@app.route("/projects")
def projects():
    conn = get_db_connection()
    data_proyek = conn.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "projects.html",
        projects=data_proyek
    )


# Menambahkan proyek baru
@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "POST":
        nama = request.form["nama"]
        deskripsi = request.form["deskripsi"]
        teknologi = request.form["teknologi"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO projects (nama, deskripsi, teknologi) VALUES (?, ?, ?)",
            (nama, deskripsi, teknologi)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("projects"))

    return render_template("tambah.html")


# Mengedit proyek
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    conn = get_db_connection()

    proyek = conn.execute(
        "SELECT * FROM projects WHERE id = ?",
        (id,)
    ).fetchone()

    if proyek is None:
        conn.close()
        return "Proyek tidak ditemukan", 404

    if request.method == "POST":
        nama = request.form["nama"]
        deskripsi = request.form["deskripsi"]
        teknologi = request.form["teknologi"]

        conn.execute(
            """UPDATE projects
               SET nama = ?, deskripsi = ?, teknologi = ?
               WHERE id = ?""",
            (nama, deskripsi, teknologi, id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("projects"))

    conn.close()
    return render_template("edit.html", project=proyek)


# Menghapus proyek
@app.route("/hapus/<int:id>", methods=["POST"])
@login_required
def hapus(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM projects WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("projects"))

# Kunci session untuk pengembangan
app.secret_key = "ganti-dengan-kunci-rahasia-kamu"

# Akun admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")


# Memeriksa apakah admin sudah login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function

# Halaman Login Admin
@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("admin"):
        return redirect(url_for("admin"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if (username == ADMIN_USERNAME and
                check_password_hash(ADMIN_PASSWORD_HASH, password)):

            session["admin"] = True
            return redirect(url_for("admin"))

        return render_template(
            "login.html",
            error="Username atau password salah!"
        )

    return render_template("login.html")


# Logout Admin
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# Dashboard Admin
@app.route("/admin")
@login_required
def admin():

    conn = get_db_connection()

    data_proyek = conn.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        projects=data_proyek
    )

# Membuat database saat program dijalankan
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
