"""
Backend do Editor de Nós Arduino/ESP32.
Requisitos: Python 3, Flask (pip install flask) e arduino-cli no PATH.
Executar:   python server.py   ->  http://localhost:5000
"""
import base64
import json
import os
import re
import shutil
import subprocess
import tempfile

from flask import Flask, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")   # ex: https://usuario.github.io


@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.route("/compile", methods=["OPTIONS"])
@app.route("/upload", methods=["OPTIONS"])
def preflight():
    return "", 204

# Lista branca de placas (evita executar FQBN arbitrário)
FQBNS = {
    "arduino:avr:uno",
    "arduino:avr:nano:cpu=atmega328",
    "arduino:avr:mega",
    "esp32:esp32:esp32",
}
PORT_RE = re.compile(r"^[\w/.\-]+$")


def cli(args, timeout=600):
    return subprocess.run(
        ["arduino-cli"] + args, capture_output=True, text=True, timeout=timeout
    )


def preparar(sketch):
    tmp = tempfile.mkdtemp(prefix="nodes_")
    pasta = os.path.join(tmp, "sketch")
    os.makedirs(pasta)
    with open(os.path.join(pasta, "sketch.ino"), "w", encoding="utf-8") as f:
        f.write(sketch)
    return tmp, pasta, os.path.join(tmp, "out")


@app.get("/")
def index():
    return send_from_directory(BASE, "index.html")


@app.post("/compile")
def compile_():
    d = request.get_json(force=True)
    fqbn, sketch = d.get("fqbn"), d.get("sketch", "")
    if fqbn not in FQBNS:
        return jsonify(ok=False, log="Placa não permitida"), 400
    tmp, pasta, out = preparar(sketch)
    try:
        r = cli(["compile", "--fqbn", fqbn, "--output-dir", out, pasta])
        log = (r.stdout or "") + (r.stderr or "")
        files = {}
        if r.returncode == 0 and os.path.isdir(out):
            for nome in os.listdir(out):
                p = os.path.join(out, nome)
                if os.path.isfile(p) and nome.endswith((".hex", ".bin")):
                    with open(p, "rb") as f:
                        files[nome] = base64.b64encode(f.read()).decode()
        return jsonify(ok=r.returncode == 0, log=log, files=files)
    except FileNotFoundError:
        return jsonify(ok=False, log="arduino-cli não encontrado no PATH"), 500
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@app.get("/ports")
def ports():
    try:
        r = cli(["board", "list", "--format", "json"], timeout=30)
        data = json.loads(r.stdout or "[]")
    except Exception as e:
        return jsonify(ok=False, ports=[], log=str(e))
    # Formatos diferentes conforme a versão do arduino-cli
    itens = data.get("detected_ports", []) if isinstance(data, dict) else data
    lista = []
    for it in itens:
        addr = (it.get("port") or {}).get("address")
        if addr:
            lista.append(addr)
    return jsonify(ok=True, ports=lista)


@app.post("/upload")
def upload():
    d = request.get_json(force=True)
    fqbn, sketch, porta = d.get("fqbn"), d.get("sketch", ""), d.get("port", "")
    if fqbn not in FQBNS:
        return jsonify(ok=False, log="Placa não permitida"), 400
    if not PORT_RE.match(porta) or porta.startswith("-"):
        return jsonify(ok=False, log="Porta inválida"), 400
    tmp, pasta, out = preparar(sketch)
    try:
        r = cli(["compile", "--upload", "-p", porta, "--fqbn", fqbn, pasta])
        return jsonify(ok=r.returncode == 0, log=(r.stdout or "") + (r.stderr or ""))
    except FileNotFoundError:
        return jsonify(ok=False, log="arduino-cli não encontrado no PATH"), 500
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", 5000)), debug=False)
