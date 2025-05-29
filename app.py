from flask import Flask, request, jsonify, render_template
import socks
import socket
import time
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def check_socks5(ip, port, user, password, timeout=5):
    try:
        start = time.time()
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, ip, int(port), True, user, password)
        s.settimeout(timeout)
        s.connect(("www.google.com", 80))
        s.close()
        response_time = int((time.time() - start) * 1000)
        return True, response_time
    except Exception:
        return False, None

@app.route('/check_proxy', methods=['POST'])
def check_proxy():
    data = request.json.get('proxy', '')
    parts = data.strip().split(':')
    if len(parts) != 4:
        return jsonify({'status':'Invalid format', 'time':'-', 'location':'Unknown'})
    ip, port, user, password = parts
    result, response_time = check_socks5(ip, port, user, password)
    # Geolocation lookup using ip-api.com (fallback to Unknown)
    loc = 'Unknown'
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=regionName,country")
        j = resp.json()
        region = j.get('regionName')
        country = j.get('country')
        if region or country:
            loc = ', '.join([p for p in [region, country] if p])
    except:
        pass
    return jsonify({
        'status': 'Working🟢' if result else 'Failed🔴',
        'time': response_time if response_time is not None else '-',
        'location': loc
    })

if __name__ == '__main__':
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

