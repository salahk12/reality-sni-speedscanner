#!/usr/bin/env bash
#
# One-command setup for the scanner's server side, on a VPS abroad.
#
# Installs Xray-core and the Python dependencies, reserves the inbound port
# range so the kernel cannot hand those ports out to outgoing connections,
# opens the firewall, and runs the scanner API as a systemd service so it
# survives a reboot. Finishes by printing the exact command to run on your own
# machine.
#
# Safe to re-run: every step checks before it acts.
#
#   sudo bash install-server.sh
#   sudo bash install-server.sh --api-port 9090 --base-port 40000 --count 1000
#
set -euo pipefail

REALITY_PORT=8443
API_PORT=8080
BASE_PORT=30000
PORT_COUNT=1000
FORCE=0
SERVICE=sniscanner

RED=$'\033[91m'; GREEN=$'\033[92m'; YELLOW=$'\033[93m'
BLUE=$'\033[94m'; CYAN=$'\033[96m'; BOLD=$'\033[1m'; RESET=$'\033[0m'

info()  { echo "${BLUE}[..]${RESET} $*"; }
ok()    { echo "${GREEN}[ok]${RESET} $*"; }
warn()  { echo "${YELLOW}[!!]${RESET} $*"; }
die()   { echo "${RED}[xx]${RESET} $*" >&2; exit 1; }

usage() {
    cat <<USAGE
Usage: sudo bash install-server.sh [options]

  --reality-port N   Reality port for legacy single-port mode (default $REALITY_PORT)
  --api-port N       Port the scanner API listens on (default $API_PORT)
  --base-port N      First port of the dedicated-inbound range (default $BASE_PORT)
  --count N          How many inbound ports to reserve and open (default $PORT_COUNT)
  --force            Continue even if a proxy panel is already running here
  -h, --help         Show this message
USAGE
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --reality-port) REALITY_PORT="$2"; shift 2 ;;
        --api-port)     API_PORT="$2";     shift 2 ;;
        --base-port)    BASE_PORT="$2";    shift 2 ;;
        --count)        PORT_COUNT="$2";   shift 2 ;;
        --force)        FORCE=1;           shift ;;
        -h|--help)      usage ;;
        *) die "unknown option: $1  (try --help)" ;;
    esac
done

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
END_PORT=$((BASE_PORT + PORT_COUNT))

echo
echo "${BOLD}Reality SNI Speed Scanner - server setup${RESET}"
echo "  repo        : $REPO_DIR"
echo "  API port    : $API_PORT"
echo "  inbound rng : $BASE_PORT-$END_PORT"
echo

# ---------------------------------------------------------------------------
# 0. Sanity
# ---------------------------------------------------------------------------
[[ $EUID -eq 0 ]] || die "run as root:  sudo bash install-server.sh"
[[ -f "$REPO_DIR/server-sniScanner.py" ]] || \
    die "server-sniScanner.py not found next to this script"

# Applying a scan config rewrites the Xray config and runs pkill -9 xray. On a
# host that is already serving proxy customers that disconnects all of them.
PANELS=""
for proc in x-ui 3x-ui hiddify marzban; do
    pgrep -x "$proc" >/dev/null 2>&1 && PANELS="$PANELS $proc"
done
if pgrep -x xray >/dev/null 2>&1 && ! systemctl is-active --quiet "$SERVICE" 2>/dev/null; then
    systemctl is-active --quiet xray 2>/dev/null || PANELS="$PANELS xray"
fi
if [[ -n "$PANELS" ]]; then
    warn "this host is already running:$PANELS"
    warn "the scanner rewrites the Xray config and restarts it, which would"
    warn "disconnect every user of that service."
    if [[ $FORCE -eq 0 ]]; then
        die "use a clean VPS, or pass --force if you are certain"
    fi
    warn "--force given, continuing anyway"
fi

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
info "checking system packages"
MISSING=""
for cmd in curl unzip lsof python3; do
    command -v "$cmd" >/dev/null 2>&1 || MISSING="$MISSING $cmd"
done
if [[ -n "$MISSING" ]]; then
    info "installing:$MISSING"
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -qq && apt-get install -y -qq $MISSING python3-pip
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y -q $MISSING python3-pip
    elif command -v yum >/dev/null 2>&1; then
        yum install -y -q $MISSING python3-pip
    else
        die "no supported package manager found; install$MISSING by hand"
    fi
fi
ok "system packages present"

# ---------------------------------------------------------------------------
# 2. Python dependencies
# ---------------------------------------------------------------------------
info "checking Python dependencies"
python3 - <<'PY' || pip3 install --quiet --break-system-packages requests PySocks 2>/dev/null \
                 || pip3 install --quiet requests PySocks
import importlib.util, sys
sys.exit(0 if all(importlib.util.find_spec(m) for m in ('requests', 'socks')) else 1)
PY
python3 -c "import requests, socks" 2>/dev/null \
    || die "could not install requests / PySocks"
ok "requests and PySocks available"

# ---------------------------------------------------------------------------
# 3. Xray-core
# ---------------------------------------------------------------------------
if [[ -x /usr/local/bin/xray ]]; then
    ok "Xray already installed: $(/usr/local/bin/xray version 2>/dev/null | head -1)"
else
    info "installing Xray-core"
    bash -c "$(curl -fsSL https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install >/dev/null
    [[ -x /usr/local/bin/xray ]] || die "Xray installation failed"
    ok "installed $(/usr/local/bin/xray version 2>/dev/null | head -1)"
fi

# ---------------------------------------------------------------------------
# 4. Reserve the inbound port range
#
# If the ephemeral range overlaps the inbound range, an outgoing connection can
# grab a port in the middle of it. Xray aborts on the first bind failure, so one
# stolen port takes down a config of a thousand inbounds.
# ---------------------------------------------------------------------------
EPHEMERAL_LOW=$(sysctl -n net.ipv4.ip_local_port_range | awk '{print $1}')
if [[ "$EPHEMERAL_LOW" -le "$END_PORT" ]]; then
    info "ephemeral ports start at $EPHEMERAL_LOW and overlap the inbound range"
    CURRENT=$(sysctl -n net.ipv4.ip_local_reserved_ports 2>/dev/null || echo "")
    if [[ "$CURRENT" == *"$BASE_PORT-$END_PORT"* ]]; then
        ok "range already reserved"
    else
        sysctl -w "net.ipv4.ip_local_reserved_ports=$BASE_PORT-$END_PORT" >/dev/null
        sed -i '/net.ipv4.ip_local_reserved_ports/d' /etc/sysctl.conf 2>/dev/null || true
        echo "net.ipv4.ip_local_reserved_ports = $BASE_PORT-$END_PORT" >> /etc/sysctl.conf
        ok "reserved $BASE_PORT-$END_PORT, persisted to /etc/sysctl.conf"
    fi
else
    ok "ephemeral range starts at $EPHEMERAL_LOW, no overlap"
fi

# ---------------------------------------------------------------------------
# 5. Firewall
# ---------------------------------------------------------------------------
OPENED=""
if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -qv inactive; then
    ufw allow "$API_PORT/tcp"                >/dev/null 2>&1 && OPENED="ufw"
    ufw allow "$BASE_PORT:$END_PORT/tcp"     >/dev/null 2>&1 || true
    ufw allow "$REALITY_PORT/tcp"            >/dev/null 2>&1 || true
fi
if command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state >/dev/null 2>&1; then
    firewall-cmd --permanent --add-port="$API_PORT/tcp"            >/dev/null 2>&1 || true
    firewall-cmd --permanent --add-port="$BASE_PORT-$END_PORT/tcp" >/dev/null 2>&1 || true
    firewall-cmd --permanent --add-port="$REALITY_PORT/tcp"        >/dev/null 2>&1 || true
    firewall-cmd --reload >/dev/null 2>&1 || true
    OPENED="$OPENED firewalld"
fi
if [[ -n "$OPENED" ]]; then
    ok "opened $API_PORT and $BASE_PORT-$END_PORT in:$OPENED"
else
    ok "no active local firewall detected"
fi
warn "if your provider has its own firewall or security group, open"
warn "TCP $API_PORT and TCP $BASE_PORT-$END_PORT there as well"

# ---------------------------------------------------------------------------
# 6. systemd service
# ---------------------------------------------------------------------------
info "installing the $SERVICE service"
systemctl stop "$SERVICE" 2>/dev/null || true
cat > "/etc/systemd/system/$SERVICE.service" <<UNIT
[Unit]
Description=Reality SNI Speed Scanner API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$REPO_DIR
ExecStart=/usr/bin/env python3 -u $REPO_DIR/server-sniScanner.py \\
    --reality-port $REALITY_PORT --api-port $API_PORT --yes
Restart=on-failure
RestartSec=5
StandardOutput=append:/var/log/$SERVICE.log
StandardError=append:/var/log/$SERVICE.log

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --quiet "$SERVICE"
systemctl reset-failed "$SERVICE" 2>/dev/null || true
systemctl start "$SERVICE"

# ---------------------------------------------------------------------------
# 7. Verify
# ---------------------------------------------------------------------------
info "waiting for the API to answer"
HEALTHY=0
for _ in $(seq 1 30); do
    if curl -fsS -m 3 "http://127.0.0.1:$API_PORT/health" >/dev/null 2>&1; then
        HEALTHY=1; break
    fi
    sleep 1
done

if [[ $HEALTHY -eq 0 ]]; then
    echo
    die "the API never came up. Check:  journalctl -u $SERVICE -n 40 --no-pager
     and:  tail -40 /var/log/$SERVICE.log"
fi

# The server shifts to a free port when the requested one is taken, so report
# the port it actually bound rather than the one we asked for.
ACTUAL_PORT=$(grep -a "API Port:" "/var/log/$SERVICE.log" 2>/dev/null \
              | tail -1 | grep -oE '[0-9]+$' || echo "$API_PORT")
PUBLIC_IP=$(curl -fsS -m 8 https://api.ipify.org 2>/dev/null || echo "<SERVER_IP>")

echo
echo "${GREEN}${BOLD}================================================================${RESET}"
echo "${GREEN}${BOLD} Server ready${RESET}"
echo "${GREEN}${BOLD}================================================================${RESET}"
echo "  address    : ${CYAN}$PUBLIC_IP:$ACTUAL_PORT${RESET}"
echo "  service    : systemctl status $SERVICE"
echo "  log        : /var/log/$SERVICE.log"
echo
echo "${BOLD}From your own machine, first check you can reach it:${RESET}"
echo "  ${CYAN}curl http://$PUBLIC_IP:$ACTUAL_PORT/health${RESET}"
echo
echo "${BOLD}Then scan:${RESET}"
echo "  ${CYAN}python client-speedScanner.py --server $PUBLIC_IP --api-port $ACTUAL_PORT \\"
echo "      --sni-file sni-1000.txt --limit 300 --workers 16 --upload-seconds 5${RESET}"
echo
echo "  If the curl times out, the port is filtered by your provider's firewall."
echo "  If it is refused, the service is not running."
echo
