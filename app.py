from flask import Flask, render_template, request
from core.auditoria_web import realizar_auditoria
from rich.console import Console
import os, pathlib

# ── Banner ──────────────────────────────────────────────
def show_banner() -> None:
    banner_file = pathlib.Path(__file__).with_name("banner.txt")
    if banner_file.exists():
        Console().print(banner_file.read_text(),
                        style="bold yellow on black")
# ─────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = ""
    if request.method == "POST":
        url     = request.form.get("url")
        method  = request.form.get("method")
        headers = request.form.get("headers")
        body    = request.form.get("body")
        fuzz    = bool(request.form.get("fuzz"))

        # Convertir headers y body si vienen en texto plano
        try:
            headers = json.loads(headers) if headers else {}
        except:
            headers = {}
        try:
            body = json.loads(body) if body else None
        except:
            body = None

        resultado = realizar_auditoria(url, method, headers, body, fuzz)

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    show_banner()                                     # ← se muestra una vez
    app.run(host="0.0.0.0", port=5000, debug=True)
