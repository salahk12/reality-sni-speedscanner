#!/usr/bin/env python3
"""
Master SNI Scanner v2.1.0 - SERVER MODE
Professional Reality SNI Testing Tool
"""

import os
import sys
import json
import subprocess
import time
import signal
import shutil
import uuid
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================================================
# SECTION 1: COLOR SETUP - Terminal color configuration
# ============================================================================

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'


def print_info(msg): print(f"{BLUE}[INFO]{RESET} {msg}")


def print_success(msg): print(f"{GREEN}[✓]{RESET} {msg}")


def print_error(msg): print(f"{RED}[✗]{RESET} {msg}")


def print_warning(msg): print(f"{YELLOW}[!]{RESET} {msg}")


# ============================================================================
# SECTION 2: GLOBAL VARIABLES
# ============================================================================

server_instance = None


# ============================================================================
# SECTION 3: PORT MANAGEMENT - Check and free ports
# ============================================================================

def check_port_available(port):
    """Check whether the port can actually be bound.

    Upstream asked this with connect_ex, which only tells you whether something
    is accepting connections. A socket that is bound but not listening, or one
    still winding down after a restart, looks free to that test and then fails
    at bind time - which is exactly the "address already in use" crash that
    killed a large multi-inbound config. Binding is both the correct question
    and faster, since it needs no timeout.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Match how the real listeners bind. Go's net.Listen and Python's
        # HTTPServer both set SO_REUSEADDR, so a port merely in TIME_WAIT is
        # usable to them; testing without it reports such a port as taken and
        # makes the server pick a different one for no reason.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False


# Killing one of these takes a whole server down with it, so never do it on the
# strength of a default port value.
PROTECTED_PROCESSES = {
    'litespeed', 'lshttpd', 'nginx', 'apache2', 'httpd', 'caddy', 'haproxy',
    'mysqld', 'mariadbd', 'postgres', 'redis-server', 'sshd', 'docker',
    'containerd', 'php-fpm', 'x-ui', '3x-ui',
}


def describe_port_owners(port):
    """Return [(pid, process name)] for whatever currently holds the port."""
    owners = []
    try:
        result = subprocess.run(f"lsof -ti:{port} -sTCP:LISTEN", shell=True,
                                capture_output=True, text=True)
        for pid in result.stdout.strip().split('\n'):
            pid = pid.strip()
            if not pid:
                continue
            name = subprocess.run(f"ps -p {pid} -o comm=", shell=True,
                                  capture_output=True, text=True).stdout.strip()
            owners.append((pid, name or 'unknown'))
    except Exception:
        pass
    return owners


def free_port(port):
    """Kill whatever holds the port, but never silently.

    The original version ran `lsof -ti:<port> | kill -9` unattended. Combined
    with the default Reality port of 443 that quietly killed the web server on
    any box that was already serving something.
    """
    owners = describe_port_owners(port)
    if not owners:
        return True

    print_warning(f"Port {port} is held by:")
    for pid, name in owners:
        print(f"    PID {pid}  {name}")

    protected = [(pid, name) for pid, name in owners
                 if name.lower() in PROTECTED_PROCESSES]
    if protected:
        print_error("Refusing to kill these automatically:")
        for pid, name in protected:
            print(f"    {name} (PID {pid})")
        print_error("This looks like a production service. Pick a different "
                    "port instead of taking it down.")
        return False

    answer = input(f"{YELLOW}Kill these and take port {port}? "
                   f"type 'yes' to confirm: {RESET}").strip().lower()
    if answer != 'yes':
        print_info("Left the port alone.")
        return False

    try:
        for pid, _ in owners:
            subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
            time.sleep(0.5)
        return True
    except Exception:
        return False


XRAY_CONFIG_PATH = '/usr/local/etc/xray/config.json'


def kill_scanner_xray():
    """Kill only the Xray this scanner started.

    `pkill -9 xray` is a substring match, so it also kills a panel's own Xray -
    x-ui runs its binary as `xray-linux-amd64`, which the pattern happily
    matches. Every config apply then disconnected that panel's customers until
    it respawned. Match on our config path instead, which nothing else uses.
    """
    killed = []
    try:
        result = subprocess.run(f"pgrep -f -- '{XRAY_CONFIG_PATH}'", shell=True,
                                capture_output=True, text=True)
        own_pid = str(os.getpid())
        for pid in result.stdout.strip().split('\n'):
            pid = pid.strip()
            if not pid or pid == own_pid:
                continue
            try:
                with open(f'/proc/{pid}/cmdline', 'rb') as handle:
                    cmdline = handle.read().decode('utf-8', 'ignore')
            except OSError:
                continue
            # Only an Xray running our config, never anything else.
            if 'xray' in cmdline.lower() and XRAY_CONFIG_PATH in cmdline:
                subprocess.run(f'kill -9 {pid}', shell=True, capture_output=True)
                killed.append(pid)
    except Exception:
        pass
    return killed


def check_not_a_production_panel():
    """Refuse to run on a box that is already serving proxy customers.

    apply_xray_config() overwrites /usr/local/etc/xray/config.json and restarts
    Xray. Even with the kill scoped to our own process, the systemd `xray` unit
    is shared, so a host already serving proxy customers is the wrong place to
    scan from. Use a clean, disposable VPS.
    """
    found = []
    for name in ('x-ui', '3x-ui', 'hiddify', 'marzban'):
        result = subprocess.run(f"pgrep -x {name}", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            found.append(name)

    # x-ui names its binary xray-linux-amd64, so an exact-name match misses it.
    xray_running = subprocess.run(
        "pgrep -af xray | grep -v -- '%s'" % XRAY_CONFIG_PATH,
        shell=True, capture_output=True, text=True).stdout.strip()
    if xray_running and not found:
        # An Xray that this script did not start is still someone's traffic.
        found.append('xray (already running)')

    if not found:
        return True

    print_error("This host is already running: " + ", ".join(found))
    print_error("The scanner rewrites the Xray config and restarts the service.")
    print_error("On a live panel that disconnects every customer on this server.")
    print_warning("Use a clean VPS for scanning instead.")
    answer = input(f"{YELLOW}Continue anyway and risk dropping live traffic? "
                   f"type 'i understand' to confirm: {RESET}").strip().lower()
    if answer != 'i understand':
        print_info("Aborted.")
        return False
    return True


def get_available_port(default_port, try_range=10):
    """Find an available port, trying a range if default is taken"""
    port = default_port
    for i in range(try_range):
        if check_port_available(port):
            return port
        else:
            port = default_port + i + 1
    return None


# ============================================================================
# SECTION 4: REQUIREMENTS & SYSTEM - Install dependencies and get system info
# ============================================================================

def install_requirements():
    """Auto-install required Python packages and Xray-core"""
    print_info("Installing requirements...")
    subprocess.run(f'{sys.executable} -m pip install requests -q', shell=True, capture_output=True)

    xray_path = '/usr/local/bin/xray'
    if not os.path.exists(xray_path):
        print_info("Installing Xray-core...")
        subprocess.run(
            'bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install',
            shell=True)
        time.sleep(3)

    print_success("Requirements check complete")


def get_server_ip():
    """Get the server's public IP address"""
    try:
        import urllib.request
        response = urllib.request.urlopen('https://api.ipify.org', timeout=5)
        return response.read().decode('utf-8').strip()
    except:
        return None


# ============================================================================
# SECTION 5: KEY MANAGEMENT - Generate keys and UUID
# ============================================================================

def generate_keys():
    """Generate x25519 keypair using xray x25519 command"""
    xray_path = '/usr/local/bin/xray'
    if not os.path.exists(xray_path):
        return None, None

    try:
        result = subprocess.run([xray_path, 'x25519'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return None, None

        output = result.stdout
        private_key = None
        public_key = None

        for line in output.split('\n'):
            line = line.strip()
            if 'Private key:' in line:
                private_key = line.split('Private key:')[1].strip()
            elif 'Public key:' in line:
                public_key = line.split('Public key:')[1].strip()
            if 'PrivateKey:' in line and not private_key:
                private_key = line.split('PrivateKey:')[1].strip()
            if 'Password (PublicKey):' in line and not public_key:
                public_key = line.split('Password (PublicKey):')[1].strip()

        if private_key and public_key:
            return private_key, public_key
        return None, None
    except Exception:
        return None, None


def generate_random_uuid():
    """Generate a cryptographically secure random UUID v4"""
    return str(uuid.uuid4())


# ============================================================================
# SECTION 6: CONFIGURATION BUILDER - Create Xray server configs
# ============================================================================

def build_stream_settings(transport_name, sni, private_key):
    """Build streamSettings for one Reality inbound dedicated to a single SNI."""
    transport_configs = {
        'tcp': {'network': 'tcp'},
        'websocket': {'network': 'ws', 'wsSettings': {'path': '/ws'}},
        'grpc': {'network': 'grpc', 'grpcSettings': {'serviceName': 'gun'}},
        'http2': {'network': 'h2', 'httpSettings': {'path': '/'}},
        'xhttp': {'network': 'xhttp', 'xhttpSettings': {'path': '/', 'mode': 'auto'}},
        'quic': {'network': 'quic'},
        'splithttp': {'network': 'splithttp', 'splithttpSettings': {'path': '/split'}}
    }
    transport = transport_configs.get(transport_name, transport_configs['tcp'])

    stream = {
        'network': transport['network'],
        'security': 'reality',
        'realitySettings': {
            'show': False,
            # Each inbound targets its own SNI. Sharing one target across many
            # serverNames makes the handshake relay fail whenever the target's
            # server rejects the mismatched SNI, which reports healthy SNIs as
            # broken.
            'target': f'{sni}:443',
            'xver': 0,
            'serverNames': [sni],
            'privateKey': private_key,
            'shortIds': ['6d6f6e6f6c697468', '']
        }
    }
    for key, value in transport.items():
        if key != 'network':
            stream[key] = value
    return stream


def create_multi_inbound_config(sni_list, base_port, private_key, transport_name, server_uuid):
    """One inbound per SNI, each with its own matching target.

    Returns (config, {sni: port}). All inbounds live in a single config so the
    whole set costs one Xray restart.
    """
    inbounds = []
    port_map = {}
    # Do not assume base_port..base_port+N is free. Anything else on the box -
    # another service, an editor's remote agent, a leftover listener - occupying
    # one port in the middle of the range makes the whole config fail to start,
    # because Xray aborts on the first bind error rather than skipping it.
    port = base_port
    for sni in sni_list:
        while not check_port_available(port):
            print_warning(f"port {port} is taken, skipping it")
            port += 1
        port_map[sni] = port
        inbounds.append({
            'port': port,
            'protocol': 'vless',
            'tag': f'reality-in-{len(inbounds)}',
            'settings': {
                'clients': [{'id': server_uuid}],
                'decryption': 'none'
            },
            'streamSettings': build_stream_settings(transport_name, sni, private_key),
            'sniffing': {'enabled': True, 'destOverride': ['http', 'tls']}
        })
        port += 1

    config = {
        'log': {'loglevel': 'warning'},
        'inbounds': inbounds,
        'outbounds': [{'protocol': 'freedom', 'tag': 'direct'}]
    }
    return config, port_map


def open_firewall_range(start_port, end_port):
    """Best effort: allow the scan port range through ufw / firewalld."""
    opened = []
    try:
        ufw = subprocess.run('ufw status', shell=True, capture_output=True, text=True)
        if ufw.returncode == 0 and 'inactive' not in ufw.stdout.lower():
            subprocess.run(f'ufw allow {start_port}:{end_port}/tcp',
                           shell=True, capture_output=True)
            opened.append('ufw')
    except Exception:
        pass
    try:
        fw = subprocess.run('firewall-cmd --state', shell=True, capture_output=True, text=True)
        if fw.returncode == 0 and 'running' in fw.stdout.lower():
            subprocess.run(f'firewall-cmd --add-port={start_port}-{end_port}/tcp',
                           shell=True, capture_output=True)
            opened.append('firewalld')
    except Exception:
        pass
    return opened


def create_server_config(port, private_key, sni_batch, transport_name, server_uuid):
    """Create Xray server configuration with specified transport"""
    transport_configs = {
        'tcp': {'network': 'tcp'},
        'websocket': {'network': 'ws', 'wsSettings': {'path': '/ws'}},
        'grpc': {'network': 'grpc', 'grpcSettings': {'serviceName': 'gun'}},
        'http2': {'network': 'h2', 'httpSettings': {'path': '/'}},
        'xhttp': {'network': 'xhttp', 'xhttpSettings': {'path': '/', 'mode': 'auto'}},
        'quic': {'network': 'quic'},
        'splithttp': {'network': 'splithttp', 'splithttpSettings': {'path': '/split'}}
    }

    transport = transport_configs.get(transport_name, transport_configs['tcp'])

    if not sni_batch or len(sni_batch) == 0:
        sni_batch = ["yahoo.com"]

    target_sni = sni_batch[0]

    reality_settings = {
        "show": False,
        "target": f"{target_sni}:443",
        "xver": 0,
        "serverNames": sni_batch,
        "privateKey": private_key,
        "shortIds": ["6d6f6e6f6c697468", ""]
    }

    inbound = {
        "port": port,
        "protocol": "vless",
        "tag": "reality-in",
        "settings": {
            "clients": [{"id": server_uuid}],
            "decryption": "none"
        },
        "streamSettings": {
            "network": transport['network'],
            "security": "reality",
            "realitySettings": reality_settings
        },
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}
    }

    for key, value in transport.items():
        if key != 'network':
            inbound['streamSettings'][key] = value

    return {
        "log": {"loglevel": "warning"},
        "inbounds": [inbound],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }


# ============================================================================
# SECTION 7: XRAY MANAGEMENT - Apply configs and manage Xray service
# ============================================================================

def wait_for_ports_free(ports, timeout=20.0):
    """Block until every port is bindable again, or give up.

    A config with 80 dedicated inbounds holds 80 listening sockets, and the
    kernel does not hand them all back the instant the process dies. Upstream
    slept one second and started the new instance regardless, which works for a
    handful of inbounds and fails with 'address already in use' for a batch.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        busy = [p for p in ports if not check_port_available(p)]
        if not busy:
            return True
        time.sleep(0.3)
    return False


def apply_xray_config(config):
    """Apply configuration to Xray and restart the service."""
    config_path = XRAY_CONFIG_PATH
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        ports = [inbound['port'] for inbound in config.get('inbounds', [])
                 if 'port' in inbound]

        subprocess.run('systemctl stop xray', shell=True, capture_output=True)
        kill_scanner_xray()

        # Wait for our own process to actually be gone before touching ports.
        deadline = time.time() + 10
        while time.time() < deadline:
            still = subprocess.run(f"pgrep -f -- '{XRAY_CONFIG_PATH}'", shell=True,
                                   capture_output=True, text=True).stdout.strip()
            if not still:
                break
            time.sleep(0.2)

        if ports and not wait_for_ports_free(ports):
            print_warning('Some ports were still bound; starting anyway')

        # Repeated failures leave the unit in 'failed' with its restart counter
        # exhausted, and systemd then refuses to start it at all until the
        # counter is cleared. Without this, one bad apply poisons every apply
        # that follows.
        subprocess.run('systemctl reset-failed xray', shell=True, capture_output=True)
        subprocess.run('systemctl start xray', shell=True, capture_output=True)

        deadline = time.time() + 15
        while time.time() < deadline:
            result = subprocess.run('systemctl is-active xray', shell=True,
                                    capture_output=True, text=True)
            state = result.stdout.strip()
            if state == 'active':
                return True
            if state == 'failed':
                break
            time.sleep(0.4)

        detail = subprocess.run(
            "journalctl -u xray -n 3 --no-pager | grep -i 'failed to' | tail -1",
            shell=True, capture_output=True, text=True).stdout.strip()
        if detail:
            print_error(f'Xray: {detail}')
        return False
    except Exception as e:
        print_error(f"Config error: {e}")
        return False


def create_minimal_config():
    """Create a minimal valid config to ensure Xray can start"""
    minimal_config = {
        "log": {"loglevel": "warning"},
        "inbounds": [],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }

    config_path = '/usr/local/etc/xray/config.json'
    os.makedirs('/usr/local/etc/xray', exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(minimal_config, f, indent=2)

    subprocess.run('systemctl stop xray', shell=True, capture_output=True)
    kill_scanner_xray()
    time.sleep(1)
    subprocess.run('systemctl reset-failed xray', shell=True, capture_output=True)
    subprocess.run('systemctl start xray', shell=True, capture_output=True)
    time.sleep(2)


# ============================================================================
# SECTION 8: HTTP API HANDLER - Handle client requests
# ============================================================================

class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler for client API requests"""

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        """Handle GET requests - health check endpoint"""
        if self.path == '/api/portmap':
            # Read-only: lets extra clients join a scan that is already set up
            # without applying a config of their own. Applying is what makes
            # concurrent clients destroy each other, since one Xray config and
            # one restart are shared by everyone.
            payload = {
                'port_map': getattr(server_instance, 'port_map', {}) or {},
                'public_key': server_instance.public_key,
                'server_uuid': server_instance.server_uuid,
                'short_id': '6d6f6e6f6c697468',
                'server_ip': server_instance.server_ip,
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'version': '2.0.0'}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests - API endpoints for config and batch management"""
        global server_instance

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                return

            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            # Endpoint: Receive SNI list from client and split into batches
            if self.path == '/api/send_config':
                sni_list = data.get('sni_list', [])
                transport = data.get('transport', 'tcp')
                batch_size = data.get('batch_size', 50)

                if not sni_list:
                    self.send_response(400)
                    self.end_headers()
                    return

                print_success(f"Received {len(sni_list)} SNI(s)")
                print_info(f"Transport: {transport}")
                print_info(f"Batch size: {batch_size}")

                batches = [sni_list[i:i + batch_size] for i in range(0, len(sni_list), batch_size)]
                print_info(f"Split into {len(batches)} batches")

                response_data = {
                    'status': 'ok',
                    'port': server_instance.port,
                    'public_key': server_instance.public_key,
                    'server_uuid': server_instance.server_uuid,
                    'short_id': '6d6f6e6f6c697468',
                    'server_ip': server_instance.server_ip,
                    'transport': transport,
                    'batches': batches,
                    'total_batches': len(batches),
                    'version': '2.0.0',
                    'api_port': server_instance.api_port
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())

            # Endpoint: Apply a specific batch to Xray
            elif self.path == '/api/apply_batch':
                sni_batch = data.get('sni_batch', [])
                transport = data.get('transport', 'tcp')
                batch_index = data.get('batch_index', 0)
                total_batches = data.get('total_batches', 1)

                if not sni_batch:
                    self.send_response(400)
                    self.end_headers()
                    return

                print_info(f"Applying batch {batch_index + 1}/{total_batches} ({len(sni_batch)} SNIs)")

                config = create_server_config(
                    server_instance.port,
                    server_instance.private_key,
                    sni_batch,
                    transport,
                    server_instance.server_uuid
                )

                if apply_xray_config(config):
                    self.send_response(200)
                    self.end_headers()
                else:
                    self.send_response(500)
                    self.end_headers()

            # Endpoint: one dedicated inbound per SNI, single Xray restart.
            elif self.path == '/api/apply_multi':
                sni_batch = data.get('sni_batch', [])
                transport = data.get('transport', 'tcp')
                base_port = int(data.get('base_port', 30000))
                chunk_index = data.get('chunk_index', 0)
                total_chunks = data.get('total_chunks', 1)

                if not sni_batch:
                    self.send_response(400)
                    self.end_headers()
                    return

                print_info(f"Applying chunk {chunk_index + 1}/{total_chunks}: "
                           f"{len(sni_batch)} dedicated inbounds from port {base_port}")

                config, port_map = create_multi_inbound_config(
                    sni_batch, base_port, server_instance.private_key,
                    transport, server_instance.server_uuid)

                opened = open_firewall_range(base_port, base_port + len(sni_batch) - 1)
                if opened:
                    print_info(f"Opened port range in: {', '.join(opened)}")

                if apply_xray_config(config):
                    server_instance.port_map = port_map
                    payload = {
                        'status': 'ok',
                        'port_map': port_map,
                        'public_key': server_instance.public_key,
                        'server_uuid': server_instance.server_uuid,
                        'short_id': '6d6f6e6f6c697468',
                        'server_ip': server_instance.server_ip,
                    }
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(payload).encode())
                else:
                    print_error("Xray failed to start with the multi-inbound config")
                    self.send_response(500)
                    self.end_headers()

            else:
                self.send_response(404)
                self.end_headers()

        except Exception as e:
            print_error(f"Request error: {e}")
            self.send_response(500)
            self.end_headers()


# ============================================================================
# SECTION 9: SERVER CLASS - Store server configuration
# ============================================================================

class Server:
    """Server configuration container"""

    def __init__(self, port, api_port, private_key, public_key, server_ip, server_uuid):
        self.port_map = {}          # SNI -> port for the config now live
        self.port = port
        self.api_port = api_port
        self.private_key = private_key
        self.public_key = public_key
        self.server_ip = server_ip
        self.server_uuid = server_uuid


# ============================================================================
# SECTION 10: SIGNAL HANDLER & MAIN - Main execution flow
# ============================================================================

def signal_handler(signum, frame):
    """Handle Ctrl+C interrupt gracefully"""
    print_info("\nShutting down server...")
    sys.exit(0)


def parse_args():
    """CLI flags so the server can run headless under nohup or systemd."""
    import argparse
    parser = argparse.ArgumentParser(description='Reality SNI Scanner - server')
    parser.add_argument('--reality-port', type=int,
                        help='Reality port for legacy shared-target mode')
    parser.add_argument('--api-port', type=int, help='HTTP API port')
    parser.add_argument('--yes', action='store_true',
                        help='Skip the production-host confirmation prompt')
    return parser.parse_args()


def main():
    """Main server execution flow"""
    global server_instance

    print(f"""
{MAGENTA}
╔══════════════════════════════════════════════════════════════════╗
║     Master SNI Scanner v2.1.0 - SERVER MODE                     ║
╚══════════════════════════════════════════════════════════════════╝
{RESET}""")

    args = parse_args()

    if os.geteuid() != 0:
        print_error("Run with: sudo python3 server-sniScanner.py")
        return

    if not args.yes and not check_not_a_production_panel():
        return

    install_requirements()

    print(f"\n{YELLOW}=== Configuration ==={RESET}")

    # Get Reality port
    if args.reality_port:
        desired_port = args.reality_port
        print_info(f"Reality port: {desired_port} (from --reality-port)")
    else:
        port_input = input(f"{CYAN}Reality port (default 443): {RESET}").strip()
        desired_port = int(port_input) if port_input.isdigit() else 443

    if not check_port_available(desired_port):
        print_warning(f"Port {desired_port} is in use, trying to free...")
        free_port(desired_port)
        time.sleep(1)

    port = get_available_port(desired_port)
    if not port:
        print_error(f"No available port near {desired_port}")
        return
    if port != desired_port:
        print_warning(f"Using port {port} instead of {desired_port}")

    # Get API port
    if args.api_port:
        desired_api_port = args.api_port
        print_info(f"API port: {desired_api_port} (from --api-port)")
    else:
        api_input = input(f"{CYAN}API port (default 8080): {RESET}").strip()
        desired_api_port = int(api_input) if api_input.isdigit() else 8080

    if not check_port_available(desired_api_port):
        print_warning(f"API port {desired_api_port} is in use, trying to free...")
        free_port(desired_api_port)
        time.sleep(1)

    api_port = get_available_port(desired_api_port)
    if not api_port:
        print_error(f"No available API port near {desired_api_port}")
        return
    if api_port != desired_api_port:
        print_warning(f"Using API port {api_port} instead of {desired_api_port}")

    # Generate keys
    print_info("Generating keys...")
    private_key, public_key = generate_keys()

    if not private_key or not public_key:
        print_warning("Could not generate keys automatically")
        private_key = input(f"{CYAN}Private Key: {RESET}").strip()
        public_key = input(f"{CYAN}Public Key: {RESET}").strip()

    if not private_key or not public_key:
        print_error("No valid keys")
        return

    print_success(f"Private Key: {private_key[:20]}...")
    print_success(f"Public Key: {public_key[:40]}...")

    # Generate UUID
    server_uuid = generate_random_uuid()
    print_success(f"Server UUID: {server_uuid}")

    # Get server IP
    server_ip = get_server_ip()
    if not server_ip:
        server_ip = input(f"{CYAN}Server IP: {RESET}").strip()

    print_success(f"Server IP: {server_ip}")

    # Initialize Xray with minimal config
    create_minimal_config()

    # Create server instance
    server_instance = Server(port, api_port, private_key, public_key, server_ip, server_uuid)
    signal.signal(signal.SIGINT, signal_handler)

    # Start HTTP server
    http_server = HTTPServer(('0.0.0.0', api_port), CustomHTTPRequestHandler)

    print(f"\n{GREEN}{'=' * 60}{RESET}")
    print(f"{GREEN}SERVER READY{RESET}")
    print(f"{GREEN}{'=' * 60}{RESET}")
    print(f"  Reality: {CYAN}{server_ip}:{port}{RESET}")
    print(f"  API Port: {CYAN}{api_port}{RESET}")
    print(f"  UUID: {CYAN}{server_uuid}{RESET}")
    print(f"\n{BLUE}Client command:{RESET}")
    print(f"{YELLOW}python3 client-sniScanner.py --server {server_ip} --api-port {api_port}{RESET}")

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()