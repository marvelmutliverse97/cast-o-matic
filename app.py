from flask import Flask, render_template, request, jsonify
import socket

app = Flask(__name__)

# Configure your classroom projector's IP address and brand here
PROJECTOR_IP = "192.168.1.50" 
PROJECTOR_BRAND = "EPSON" # Change to "BENQ" if needed

def send_epson_command(command_str):
    """Sends ESC/VP.net command to Epson projectors over TCP port 3629"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect((PROJECTOR_IP, 3629))
            s.sendall((command_str + "\r").encode('ascii'))
            response = s.recv(1024).decode('ascii')
            return True, response
    except Exception as e:
        return False, str(e)

def send_benq_pjlink_command(command_str):
    """Sends PJLink command to BenQ projectors over TCP port 4352"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect((PROJECTOR_IP, 4352))
            s.sendall((command_str + "\r").encode('ascii'))
            response = s.recv(1024).decode('ascii')
            return True, response
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html', ip=PROJECTOR_IP, brand=PROJECTOR_BRAND)

@app.route('/control', methods=['POST'])
def control():
    data = request.json
    action = data.get('action')
    value = data.get('value')

    success = False
    msg = ""

    if PROJECTOR_BRAND == "EPSON":
        if action == 'power':
            cmd = "PWR ON" if value == "ON" else "PWR OFF"
            success, msg = send_epson_command(cmd)
        elif action == 'input':
            cmd = "SOURCE 11" if value == "HDMI 1" else "SOURCE 41"
            success, msg = send_epson_command(cmd)

    elif PROJECTOR_BRAND == "BENQ":
        if action == 'power':
            cmd = "%1POWR 1" if value == "ON" else "%1POWR 0"
            success, msg = send_benq_pjlink_command(cmd)
        elif action == 'input':
            cmd = "%1INPT 31" if value == "HDMI 1" else "%1INPT 51"
            success, msg = send_benq_pjlink_command(cmd)

    return jsonify({"success": success, "response": msg, "action": action, "value": value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5080, debug=True)