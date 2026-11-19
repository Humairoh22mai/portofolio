
import os

from flask import (
    Flask, render_template, request,
    redirect, url_for, session
)

from functools import wraps
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from dotenv import load_dotenv
from supabase import create_client


# Membaca konfigurasi dari file .env
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "kunci-pengembangan-ganti-saat-deploy"
)


# =====================================
# KONEKSI SUPABASE
# =====================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL dan SUPABASE_KEY belum diatur."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =====================================
# AKUN ADMIN
# =====================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# =====================================
# HALAMAN HOME
# =====================================

@app.route("/")
def index():
    hasil = (
        supabase.table("projects")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    data_proyek = hasil.data or []

    return render_template(
        "index.html",
        projects=data_proyek
    )


# =====================================
# HALAMAN ABOUT
# =====================================

@app.route("/about")
def about():
    return render_template("about.html")


# =====================================
# HALAMAN PROJECTS
# =====================================

@app.route("/projects")
def projects():
    hasil = (
        supabase.table("projects")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    data_proyek = hasil.data or []

    return render_template(
        "projects.html",
        projects=data_proyek
    )


# =====================================
# TAMBAH PROYEK
# =====================================

@app.route("/tambah", methods=["GET", "POST"])
@login_required
def tambah():

    if request.method == "POST":

        nama = request.form["nama"]
        deskripsi = request.form["deskripsi"]
        teknologi = request.form["teknologi"]
        link_proyek = request.form.get("link_proyek") or None

        supabase.table("projects").insert({
            "nama": nama,
            "deskripsi": deskripsi,
            "teknologi": teknologi,
            "link_proyek": link_proyek
        }).execute()

        return redirect(url_for("admin"))

    return render_template("tambah.html")


# =====================================
# EDIT PROYEK
# =====================================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):

    hasil = (
        supabase.table("projects")
        .select("*")
        .eq("id", id)
        .limit(1)
        .execute()
    )

    data = hasil.data or []

    if not data:
        return "Proyek tidak ditemukan", 404

    proyek = data[0]

    if request.method == "POST":

        nama = request.form["nama"]
        deskripsi = request.form["deskripsi"]
        teknologi = request.form["teknologi"]
        link_proyek = request.form.get("link_proyek") or None

        supabase.table("projects").update({
            "nama": nama,
            "deskripsi": deskripsi,
            "teknologi": teknologi,
            "link_proyek": link_proyek
        }).eq("id", id).execute()

        return redirect(url_for("admin"))

    return render_template(
        "edit.html",
        project=proyek
    )


# =====================================
# HAPUS PROYEK
# =====================================

@app.route("/hapus/<int:id>", methods=["POST"])
@login_required
def hapus(id):

    supabase.table("projects").delete().eq(
        "id", id
    ).execute()

    return redirect(url_for("admin"))


# =====================================
# LOGIN ADMIN
# =====================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("admin"):
        return redirect(url_for("admin"))

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if (
            username == ADMIN_USERNAME
            and check_password_hash(
                ADMIN_PASSWORD_HASH, password
            )
        ):
            session["admin"] = True
            return redirect(url_for("admin"))

        return render_template(
            "login.html",
            error="Username atau password salah!"
        )

    return render_template("login.html")


# =====================================
# LOGOUT ADMIN
# =====================================

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


# =====================================
# DASHBOARD ADMIN
# =====================================

@app.route("/admin")
@login_required
def admin():

    hasil = (
        supabase.table("projects")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    data_proyek = hasil.data or []

    return render_template(
        "admin.html",
        projects=data_proyek
    )


# =====================================
# MENJALANKAN APLIKASI
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
