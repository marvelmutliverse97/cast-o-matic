import os
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import (
    Flask, render_template, request, jsonify,
    send_from_directory
)
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "cast-o-matic-secret"
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

# State variables updated dynamically by the auto-discovery scanner
PROJECTOR_IP = "192.168.1.50"
PROJECTOR_BRAND = "AUTO-DETECT"
PROJECTOR_PORT = 3629

ROOM = "classroom"
current_presentation = None


def scan_ip(ip):
    """Checks for open projector communication ports across the network."""
    # Check Epson port (3629)
    try:
        with socket.create_connection((str(ip), 3629), timeout=0.2):
            return str(ip), "EPSON", 3629
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass

    # Check PJLink standard port (4352) - used by BenQ, Sony, Panasonic, etc.
    try:
        with socket.create_connection((str(ip), 4352), timeout=0.2):
            return str(ip), "PJLINK", 4352
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass

    return None, None, None


def discover_projector_ip():
    """Scans subnet, discovers any active projector, and dynamically updates its brand."""
    global PROJECTOR_IP, PROJECTOR_BRAND, PROJECTOR_PORT
    print("Scanning local network for any active projectors...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        subnet_prefix = ".".join(local_ip.split(".")[:3]) + "."
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(scan_ip, subnet_prefix + str(i)): i for i in range(1, 255)}
            for future in as_completed(futures):
                found_ip, proto_type, port = future.result()
                if found_ip:
                    PROJECTOR_IP = found_ip
                    PROJECTOR_PORT = port
                    
                    if proto_type == "EPSON":
                        PROJECTOR_BRAND = "EPSON"
                    elif proto_type == "PJLINK":
                        # Dynamically query the exact manufacturer name from the device
                        try:
                            with socket.create_connection((found_ip, port), timeout=1.0) as conn:
                                conn.settimeout(1.0)
                                try:
                                    conn.recv(1024)  # Consume initial greeting
                                except socket.timeout:
                                    pass
                                conn.sendall(b"%1INF1 ?\r")
                                resp = conn.recv(1024).decode("ascii", errors="replace").strip()
                                if "=" in resp:
                                    PROJECTOR_BRAND = resp.split("=")[1].strip().upper()
                                else:
                                    PROJECTOR_BRAND = "UNIVERSAL"
                        except Exception:
                            PROJECTOR_BRAND = "UNIVERSAL"
                            
                    print(f"Projector discovered! Brand: {PROJECTOR_BRAND} at IP: {found_ip}:{port}")
                    return found_ip
    except Exception as e:
        print(f"Auto-discovery network scan failed: {e}")
    
    print(f"Projector not found automatically. Falling back to default -> IP: {PROJECTOR_IP}, Brand: {PROJECTOR_BRAND}")
    return PROJECTOR_IP


def send_projector_command(action, value):
    """Sends control commands adapted dynamically to the detected projector brand."""
    global PROJECTOR_BRAND, PROJECTOR_PORT, PROJECTOR_IP

    if PROJECTOR_BRAND == "EPSON":
        if action == "power":
            command = "PWR ON" if value == "ON" else "PWR OFF"
        elif action == "input":
            command = "SOURCE 11" if value == "HDMI 1" else "SOURCE 41"
        else:
            return False, "Invalid action"
        payload = (command + "\r").encode("ascii")

    else:  # Standard PJLink protocol used by BenQ, Sony, Panasonic, etc.
        if action == "power":
            pw_val = "1" if value == "ON" else "0"
            command = f"%1POWR {pw_val}"
        elif action == "input":
            in_val = "31" if value == "HDMI 1" else "51"
            command = f"%1INPT {in_val}"
        else:
            return False, "Invalid action"
        payload = (command + "\r").encode("ascii")

    try:
        with socket.create_connection(
            (PROJECTOR_IP, PROJECTOR_PORT),
            timeout=1.5
        ) as connection:
            if PROJECTOR_BRAND != "EPSON":
                try:
                    connection.recv(1024)  # Consume PJLink greeting if present
                except socket.timeout:
                    pass
            connection.sendall(payload)
            response = connection.recv(1024).decode("ascii", errors="replace")
            return True, response

    except (socket.timeout, ConnectionRefusedError, OSError) as error:
        return False, f"Projector offline ({error})"


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route("/")
def index():
    return render_template(
        "index.html",
        ip=PROJECTOR_IP,
        brand=PROJECTOR_BRAND
    )


@app.route("/sender")
def sender():
    return render_template("sender.html")


@app.route("/receiver")
def receiver():
    return render_template(
        "receiver.html",
        presentation=current_presentation
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    global current_presentation

    if "file" not in request.files:
        return jsonify(
            success=False,
            error="No file was selected"
        ), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify(
            success=False,
            error="Please select a PDF file"
        ), 400

    filename = secure_filename(file.filename)

    if not filename or not filename.lower().endswith(".pdf"):
        return jsonify(
            success=False,
            error="Only PDF files are supported"
        ), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)

        with open(filepath, "rb") as pdf:
            if not pdf.read(5).startswith(b"%PDF-"):
                os.remove(filepath)
                return jsonify(
                    success=False,
                    error="Invalid PDF file"
                ), 400

        current_presentation = filename

        socketio.emit(
            "presentation_update",
            {"filename": filename},
            to=ROOM
        )

        return jsonify(
            success=True,
            filename=filename
        )

    except OSError as error:
        app.logger.exception("Upload failed")
        return jsonify(
            success=False,
            error=str(error)
        ), 500


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=False
    )


@app.route("/control", methods=["POST"])
def control():
    data = request.get_json(silent=True) or {}

    action = data.get("action")
    value = data.get("value")

    if action == "power" and value not in ("ON", "OFF"):
        return jsonify(success=False, error="Invalid power command"), 400

    if action == "input" and value not in ("HDMI 1", "Wireless Cast"):
        return jsonify(success=False, error="Invalid input source"), 400

    if action not in ("power", "input"):
        return jsonify(success=False, error="Unknown control action"), 400

    success, response = send_projector_command(action, value)

    return jsonify(
        success=success,
        response=response,
        action=action,
        value=value,
        brand=PROJECTOR_BRAND
    ), (200 if success else 502)


@socketio.on("join")
def on_join(data):
    from flask_socketio import join_room
    room = (data or {}).get("room", ROOM)
    if room != ROOM:
        return
    join_room(room)
    print("Client joined casting room:", room)


@socketio.on("offer")
def handle_offer(data):
    data = data or {}
    if data.get("room") != ROOM:
        return
    print("Relaying WebRTC offer")
    emit("offer", data.get("offer"), to=ROOM, include_self=False)


@socketio.on("answer")
def handle_answer(data):
    data = data or {}
    if data.get("room") != ROOM:
        return
    print("Relaying WebRTC answer")
    emit("answer", data.get("answer"), to=ROOM, include_self=False)


@socketio.on("ice-candidate")
def handle_ice_candidate(data):
    data = data or {}
    if data.get("room") != ROOM:
        return

    candidate = data.get("candidate", data)
    if isinstance(candidate, dict):
        cand_str = candidate.get("candidate")
        if cand_str:
            emit("ice-candidate", data, to=ROOM, include_self=False)


@app.errorhandler(413)
def file_too_large(error):
    return jsonify(
        success=False,
        error="File exceeds the 50 MB upload limit"
    ), 413


if __name__ == "__main__":
    # Scan network and update brand dynamically on startup
    discover_projector_ip()

    socketio.run(
        app,
        host="0.0.0.0",
        port=5080,
        debug=False
    )