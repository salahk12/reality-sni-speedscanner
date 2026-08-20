#!/usr/bin/env python3
"""
Reality SNI Speed Scanner - CLIENT
==================================
Fork of Master Reality SNI Scanner (AminDaProgrammer) with a second stage that
measures real download / upload throughput, latency and jitter through the
Reality tunnel, plus fixes for the parallel-scan port collision in upstream.

Probes run in parallel; each one that succeeds is handed to a single uploader
thread that measures throughput serially. Upload tests must stay serial - two
concurrent transfers contend for the same last-mile bandwidth and both numbers
come out wrong - but queueing them behind parallel probes means results start
arriving immediately instead of after the whole list has been probed.
"""

import os
import sys
import json
import csv
import time
import math
import socket
import signal
import random
import platform
import argparse
import tempfile
import threading
import queue
import itertools
import statistics
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests

# ============================================================================
# SECTION 1: TERMINAL COLORS
# ============================================================================

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'


def setup_colors():
    """Enable ANSI colors on Windows consoles."""
    if platform.system().lower() == 'windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


setup_colors()


def print_info(msg): print(f"{BLUE}[INFO]{RESET} {msg}")


def print_success(msg): print(f"{GREEN}[OK]{RESET} {msg}")


def print_error(msg): print(f"{RED}[X]{RESET} {msg}")


def print_warning(msg): print(f"{YELLOW}[!]{RESET} {msg}")


def print_step(title):
    print(f"\n{YELLOW}{BOLD}{'=' * 68}{RESET}")
    print(f"{YELLOW}{BOLD}{title}{RESET}")
    print(f"{YELLOW}{BOLD}{'=' * 68}{RESET}")


def print_banner():
    print(f"""{MAGENTA}{BOLD}
+==================================================================+
|   Reality SNI Speed Scanner  -  CLIENT                           |
|   reachability + latency + download/upload benchmark             |
+==================================================================+{RESET}
""")


# ============================================================================
# SECTION 2: SPEED TEST ENDPOINTS (Cloudflare)
# ============================================================================

SPEED_HOST = 'https://speed.cloudflare.com'
DOWN_URL = SPEED_HOST + '/__down?bytes={bytes}'
UP_URL = SPEED_HOST + '/__up'
PING_URL = SPEED_HOST + '/__down?bytes=0'

# requests treats a scalar timeout as both the connect and the read budget, so
# a dead tunnel burns the full value before failing. Splitting them lets the
# connect phase fail fast while still allowing a long wait for the response of a
# transfer that is genuinely in progress.
CONNECT_TIMEOUT = 5.0


def rw_timeout(read_seconds):
    """(connect, read) timeout pair for a request through the tunnel."""
    return (CONNECT_TIMEOUT, read_seconds)


# One megabyte of incompressible data, reused for every upload test.
_UPLOAD_BLOB = os.urandom(1024 * 1024)


# ============================================================================
# SECTION 3: LOCAL PORT ALLOCATION
#
# Upstream hardcoded the SOCKS inbound to port 1080 for every worker, so
# parallel workers fought over one port and killed each other's Xray. Each
# worker now gets its own port.
# ============================================================================

_port_lock = threading.Lock()
_port_counter = itertools.count(random.randint(10800, 20000))


def _port_is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False


def alloc_local_port():
    """Reserve a free loopback port for one Xray SOCKS inbound."""
    with _port_lock:
        for _ in range(2000):
            port = next(_port_counter)
            if port > 62000:
                globals()['_port_counter'] = itertools.count(10800)
                continue
            if _port_is_free(port):
                return port
    raise RuntimeError('no free local port available')


# ============================================================================
# SECTION 4: XRAY PROCESS MANAGEMENT
# ============================================================================

def get_xray_path():
    """Locate the Xray executable."""
    import shutil
    if platform.system().lower() == 'windows':
        candidates = [r'C:\Program Files\xray\xray.exe', r'C:\xray\xray.exe',
                      os.path.join(os.getcwd(), 'xray.exe')]
    else:
        candidates = ['/usr/local/bin/xray', '/usr/bin/xray',
                      os.path.join(os.getcwd(), 'xray')]
    for path in candidates:
        if os.path.exists(path):
            return path
    return shutil.which('xray')


def kill_all_xray():
    """Kill every Xray process. Only used at shutdown, never per worker."""
    if platform.system().lower() == 'windows':
        subprocess.run('taskkill /f /im xray.exe', shell=True, capture_output=True)
    else:
        subprocess.run('pkill -9 xray', shell=True, capture_output=True)


class XrayTunnel:
    """Run one Xray client instance exposing a private SOCKS5 port.

    Used as a context manager so the process and its temp config are always
    reaped, including on exceptions and Ctrl+C.
    """

    def __init__(self, config, socks_port, startup_timeout=6.0):
        self.config = config
        self.socks_port = socks_port
        self.startup_timeout = startup_timeout
        self.process = None
        self.config_path = None

    @property
    def proxies(self):
        # socks5h keeps DNS resolution inside the tunnel; plain socks5 would
        # resolve names with the local (censored) resolver.
        url = f'socks5h://127.0.0.1:{self.socks_port}'
        return {'http': url, 'https': url}

    def __enter__(self):
        xray_path = get_xray_path()
        if not xray_path:
            raise RuntimeError('xray executable not found')

        fd, self.config_path = tempfile.mkstemp(suffix='.json', prefix='sniscan_')
        with os.fdopen(fd, 'w') as handle:
            json.dump(self.config, handle)

        kwargs = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if platform.system().lower() == 'windows':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        else:
            kwargs['start_new_session'] = True

        self.process = subprocess.Popen([xray_path, 'run', '-c', self.config_path], **kwargs)

        # Poll until the SOCKS port accepts connections instead of sleeping a
        # fixed interval: faster on a good machine, more reliable on a slow one.
        deadline = time.time() + self.startup_timeout
        while time.time() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError('xray exited during startup')
            try:
                with socket.create_connection(('127.0.0.1', self.socks_port), timeout=0.3):
                    return self
            except OSError:
                time.sleep(0.08)
        raise RuntimeError('xray SOCKS port did not open in time')

    def __exit__(self, exc_type, exc_value, traceback):
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                    self.process.wait(timeout=3)
                except Exception:
                    pass
        if self.config_path and os.path.exists(self.config_path):
            try:
                os.unlink(self.config_path)
            except OSError:
                pass
        return False


# ============================================================================
# SECTION 5: XRAY CLIENT CONFIG BUILDER
# ============================================================================

# Transport name as used by the API/UI -> value used in a vless:// URI.
URI_TYPE = {
    'tcp': 'tcp', 'websocket': 'ws', 'grpc': 'grpc', 'http2': 'h2',
    'xhttp': 'xhttp', 'quic': 'quic', 'splithttp': 'splithttp',
}


def apply_transport(stream_settings, transport):
    """Fill streamSettings for the chosen transport."""
    if transport == 'websocket':
        stream_settings['network'] = 'ws'
        stream_settings['wsSettings'] = {'path': '/ws'}
    elif transport == 'grpc':
        stream_settings['network'] = 'grpc'
        stream_settings['grpcSettings'] = {'serviceName': 'gun'}
    elif transport == 'http2':
        stream_settings['network'] = 'h2'
        stream_settings['httpSettings'] = {'path': '/'}
    elif transport == 'xhttp':
        stream_settings['network'] = 'xhttp'
        stream_settings['xhttpSettings'] = {'path': '/', 'mode': 'auto'}
    elif transport == 'quic':
        stream_settings['network'] = 'quic'
    elif transport == 'splithttp':
        stream_settings['network'] = 'splithttp'
        stream_settings['splithttpSettings'] = {'path': '/split'}
    else:
        stream_settings['network'] = 'tcp'
    return stream_settings


def create_xray_config(server, sni, socks_port, remote_port=None):
    """Build a client config with a SOCKS inbound on the given private port."""
    stream_settings = {
        'network': 'tcp',
        'security': 'reality',
        'realitySettings': {
            'serverName': sni,
            'fingerprint': 'chrome',
            'publicKey': server['public_key'],
            'shortId': server['short_id'],
        },
    }
    apply_transport(stream_settings, server['transport'])

    outbound = {
        'protocol': 'vless',
        'tag': 'proxy',
        'settings': {
            'vnext': [{
                'address': server['server_ip'],
                'port': remote_port or server['port'],
                'users': [{'id': server['server_uuid'], 'encryption': 'none'}],
            }]
        },
        'streamSettings': stream_settings,
    }

    return {
        'log': {'loglevel': 'none'},
        'inbounds': [{
            'listen': '127.0.0.1',
            'port': socks_port,
            'protocol': 'socks',
            'settings': {'udp': True, 'auth': 'noauth'},
        }],
        'outbounds': [outbound, {'protocol': 'freedom', 'tag': 'direct'}],
    }


def build_link(server, sni, remote_port=None):
    """Build an importable vless:// URI for this SNI."""
    uri_type = URI_TYPE.get(server['transport'], 'tcp')
    port = remote_port or server['port']
    params = (
        f"type={uri_type}&security=reality&encryption=none"
        f"&pbk={server['public_key']}&fp=chrome&sni={sni}&sid={server['short_id']}"
    )
    if uri_type == 'ws':
        params += '&path=%2Fws'
    elif uri_type == 'grpc':
        params += '&serviceName=gun'
    elif uri_type in ('h2', 'xhttp', 'splithttp'):
        params += '&path=%2F'
    return (f"vless://{server['server_uuid']}@{server['server_ip']}:{port}"
            f"?{params}#Reality_{sni}")


# ============================================================================
# SECTION 6: STAGE 1 - REACHABILITY + LATENCY PROBE
# ============================================================================

_results_lock = threading.Lock()
_print_lock = threading.Lock()
_stage1_results = []
_stage2_results = []
_scan_state = {'completed': False, 'server': None}


def probe_sni(server, sni, batch_index, remote_port=None, timeout=6):
    """Check whether this SNI produces a working tunnel and measure latency."""
    record = {'sni': sni, 'batch_index': batch_index, 'success': False,
              'latency': None, 'remote_port': remote_port, 'link': None, 'error': None}
    try:
        socks_port = alloc_local_port()
        config = create_xray_config(server, sni, socks_port, remote_port)
        with XrayTunnel(config, socks_port) as tunnel:
            # Two samples, keep the best. The first connection through a fresh
            # tunnel also pays for the server's cold handshake to the target,
            # which can add seconds and would wrongly sink a good SNI's rank.
            latencies = []
            status = None
            for _ in range(2):
                started = time.time()
                response = requests.get(PING_URL, proxies=tunnel.proxies,
                                        timeout=rw_timeout(timeout))
                latencies.append(int((time.time() - started) * 1000))
                status = response.status_code
            if status is not None and status < 400:
                record.update(success=True, latency=min(latencies),
                              link=build_link(server, sni, remote_port))
            else:
                record['error'] = f'HTTP {status}'
    except Exception as exc:
        record['error'] = type(exc).__name__
    return record


def run_stage1(server, sni_batch, batch_index, max_workers, port_map=None):
    """Probe a batch of SNIs in parallel. Each worker gets its own SOCKS port."""
    results = []
    port_map = port_map or {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(probe_sni, server, sni, batch_index,
                                   port_map.get(sni)): sni
                   for sni in sni_batch}
        for future in as_completed(futures):
            record = future.result()
            results.append(record)
            with _results_lock:
                _stage1_results.append(record)
            if record['success']:
                print(f"  {GREEN}OK{RESET}   {record['sni']:<42} {record['latency']:>5} ms")
            else:
                print(f"  {DIM}fail {record['sni']:<42} {record['error'] or ''}{RESET}")
    return results


# ============================================================================
# SECTION 7: STAGE 2 - THROUGHPUT / JITTER BENCHMARK
# ============================================================================

def measure_latency_samples(proxies, samples=5, timeout=8):
    """Return (min_ms, avg_ms, jitter_ms) from repeated zero-byte requests.

    One warm-up request is sent and discarded first. It carries the server's
    cold handshake to the Reality target, which is a one-off cost and would
    otherwise dominate the jitter figure.
    """
    values = []
    for index in range(samples + 1):
        try:
            started = time.time()
            requests.get(PING_URL, proxies=proxies, timeout=rw_timeout(timeout))
            elapsed = (time.time() - started) * 1000
            if index > 0:
                values.append(elapsed)
        except Exception:
            pass
        time.sleep(0.05)
    if not values:
        return None, None, None
    jitter = statistics.stdev(values) if len(values) > 1 else 0.0
    return round(min(values), 1), round(statistics.fmean(values), 1), round(jitter, 1)


def measure_download(proxies, size_mb, time_cap):
    """Download through the tunnel and return Mbps.

    Timing starts at the first received chunk so the TLS handshake and TTFB do
    not deflate the throughput figure.
    """
    total_bytes = size_mb * 1024 * 1024
    try:
        response = requests.get(DOWN_URL.format(bytes=total_bytes), proxies=proxies,
                                stream=True, timeout=rw_timeout(time_cap + 8))
        received = 0
        started = None
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            if started is None:
                started = time.time()
                continue  # exclude the first chunk: it carries the TTFB
            received += len(chunk)
            if time.time() - started > time_cap:
                break
        response.close()
        if started is None or received == 0:
            return None
        elapsed = time.time() - started
        if elapsed <= 0:
            return None
        return round((received * 8) / elapsed / 1_000_000, 2)
    except Exception:
        return None


def _post_fixed(session, proxies, payload, read_timeout):
    """POST a fixed-length body. Returns (bytes_sent, seconds) or None.

    The body must be a sized object, never a generator. requests falls back to
    chunked transfer encoding for generator bodies, and on that code path
    urllib3 never applies the timeout to the socket: a tunnel that accepts the
    connection but never completes the TLS handshake blocks forever instead of
    failing. Measured against a deliberately stalling proxy, a bytes body failed
    in 5 seconds while the identical request with a generator body was still
    hanging after 75.
    """
    try:
        started = time.time()
        response = session.post(
            UP_URL, data=payload, proxies=proxies,
            timeout=rw_timeout(read_timeout),
            headers={'Content-Type': 'application/octet-stream'})
        elapsed = time.time() - started
        if response.status_code >= 400 or elapsed <= 0:
            return None
        return len(payload), elapsed
    except Exception:
        return None


def _mbps(byte_count, seconds):
    return round((byte_count * 8) / seconds / 1_000_000, 2)


def measure_upload(proxies, size_mb, time_cap):
    """Upload through the tunnel and return Mbps.

    Sizing the payload matters in both directions: too small and a fast link is
    measured entirely inside TCP slow start, too large and a slow uplink stalls
    for minutes on a single SNI. So a small calibration upload sets the rate,
    and the real sample is sized to land near `time_cap` at that rate.
    """
    calibration_bytes = 512 * 1024
    # One session for both uploads so the second reuses the warmed TCP
    # connection instead of paying for slow start all over again.
    session = requests.Session()
    try:
        first = _post_fixed(session, proxies, _UPLOAD_BLOB[:calibration_bytes],
                            read_timeout=min(20.0, time_cap + 5))
        if first is None:
            return None
        sent, elapsed = first

        target = int((sent / elapsed) * time_cap)
        target = max(calibration_bytes, min(target, size_mb * 1024 * 1024))

        # On a slow link the calibration upload already took a meaningful slice
        # of the budget, so a second pass would only repeat it.
        if target <= calibration_bytes * 2:
            return _mbps(sent, elapsed)

        repeats = (target // len(_UPLOAD_BLOB)) + 1
        payload = (_UPLOAD_BLOB * repeats)[:target]
        second = _post_fixed(session, proxies, payload, read_timeout=time_cap + 10)
        if second is None:
            return _mbps(sent, elapsed)      # keep the calibration figure
        return _mbps(*second)
    finally:
        session.close()


def benchmark_sni(server, sni, args, remote_port=None, known_latency=None,
                  measure_latency=True):
    """Benchmark one SNI. Callers must invoke this serially.

    When `known_latency` is supplied the probe already measured it, so this only
    moves bytes. Re-measuring latency here would cost several seconds per SNI to
    reproduce a number we already have.
    """
    record = {'sni': sni, 'link': build_link(server, sni, remote_port),
              'remote_port': remote_port, 'reachable': False,
              'latency_min': known_latency, 'latency_avg': known_latency,
              'jitter': None, 'download_mbps': None, 'upload_mbps': None,
              'error': None}
    try:
        socks_port = alloc_local_port()
        config = create_xray_config(server, sni, socks_port, remote_port)
        with XrayTunnel(config, socks_port) as tunnel:
            proxies = tunnel.proxies

            if measure_latency and known_latency is None:
                lat_min, lat_avg, jitter = measure_latency_samples(proxies,
                                                                   args.ping_samples)
                if lat_min is None:
                    record['error'] = 'no latency response'
                    return record
                record.update(latency_min=lat_min, latency_avg=lat_avg, jitter=jitter)
            record['reachable'] = True

            record['upload_mbps'] = measure_upload(proxies, args.upload_mb,
                                                   args.upload_seconds)

            # Download is off by default: per-SNI shaping shows up on the upload
            # path first, and skipping it halves both the runtime and the bill.
            if args.with_download:
                download = measure_download(proxies, args.download_mb, args.time_cap)
                # A fast link drains the sample before the time cap; repeat with
                # a bigger payload so the number reflects steady state rather
                # than TCP slow start.
                if download is not None and args.download_mb < args.max_download_mb:
                    if (args.download_mb * 8) / download < args.time_cap * 0.6:
                        bigger = measure_download(proxies, args.max_download_mb,
                                                  args.time_cap)
                        if bigger is not None:
                            download = bigger
                record['download_mbps'] = download
    except Exception as exc:
        record['error'] = type(exc).__name__
    return record


def run_stage2(server, finalists, args, port_map=None):
    """Benchmark a list serially. Used by the two-phase (--phased) path."""
    results = []
    port_map = port_map or {}
    total = len(finalists)
    for index, sni in enumerate(finalists, 1):
        print(f"  {CYAN}[{index}/{total}]{RESET} {sni} ...", end='', flush=True)
        record = benchmark_sni(server, sni, args, port_map.get(sni))
        results.append(record)
        with _results_lock:
            _stage2_results.append(record)
        print('\r' + format_result_line(record, index, total, args))
    return results


def format_result_line(record, index, total, args):
    """One finished SNI, rendered for the live log."""
    if not record['reachable'] or record['upload_mbps'] is None:
        return (f"  {RED}[{index}/{total}]{RESET} {record['sni']:<40} failed "
                f"({record.get('error') or 'no upload'})")
    up = f"{record['upload_mbps']:.2f}"
    line = (f"  {GREEN}[{index}/{total}]{RESET} {record['sni']:<40}"
            f"U {up:>9} Mbps  "
            f"{record['latency_min'] if record['latency_min'] else '-':>5} ms")
    if record.get('jitter') is not None:
        line += f"  jit {record['jitter']:>5} ms"
    if args.with_download and record.get('download_mbps'):
        line += f"  D {record['download_mbps']:>9.2f} Mbps"
    return line


def run_pipelined(server, sni_list, chunk_index, args, port_map=None):
    """Probe in parallel and upload-test serially, at the same time.

    Probes are cheap and parallel; upload tests are expensive and must stay
    serial or they fight each other for the uplink. Running them as two separate
    phases means no throughput number appears until every probe has finished.
    Here each probe that succeeds is handed straight to a single uploader
    thread, so results start arriving almost immediately and a Ctrl+C at any
    point leaves a useful set of measurements behind.

    The uplink is busy while probes run, so probe latency is measured under load
    and reads higher than an idle ping. Use --phased if you want clean latency.
    """
    port_map = port_map or {}
    pending = queue.Queue()
    results = []
    counters = {'done': 0, 'reachable': 0}
    total = len(sni_list)

    def uploader():
        while True:
            item = pending.get()
            if item is None:
                pending.task_done()
                return
            try:
                counters['done'] += 1
                record = benchmark_sni(server, item['sni'], args,
                                       item.get('remote_port'),
                                       known_latency=item['latency'],
                                       measure_latency=False)
                results.append(record)
                with _results_lock:
                    _stage2_results.append(record)
                with _print_lock:
                    # Denominator is the chunk size, not the reachable count:
                    # the latter is still growing while probes run and a moving
                    # denominator reads like a bug.
                    print(format_result_line(record, counters['done'], total, args))
            except Exception as exc:
                with _print_lock:
                    print_error(f"{item['sni']}: {type(exc).__name__}")
            finally:
                pending.task_done()

    worker = threading.Thread(target=uploader, daemon=True)
    worker.start()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(probe_sni, server, sni, chunk_index,
                                   port_map.get(sni)): sni for sni in sni_list}
        for future in as_completed(futures):
            record = future.result()
            with _results_lock:
                _stage1_results.append(record)
            if record['success']:
                counters['reachable'] += 1
                pending.put(record)
            elif args.probe_gate:
                with _print_lock:
                    print(f"  {DIM}ping fail  {record['sni']:<40}"
                          f"{record['error'] or ''}{RESET}")
            else:
                # The probe is an HTTP request to speed.cloudflare.com through
                # the tunnel, not a ping to the SNI. On a slow or lossy link it
                # can time out while the tunnel is perfectly usable, so a failed
                # probe is a missing latency reading, not a verdict. Measure the
                # upload anyway and let that decide.
                counters['reachable'] += 1
                pending.put(record)

    with _print_lock:
        remaining = pending.unfinished_tasks
        if remaining:
            print_info(f'probes done; {remaining} upload test(s) still queued')

    pending.put(None)
    worker.join()
    return results


# ============================================================================
# SECTION 8: SCORING
# ============================================================================

def score_results(results):
    """Rank benchmarked SNIs on a 0-100 composite score.

    Upload dominates. Per-SNI shaping bites the upload path hardest, and an SNI
    whose upload has been throttled is useless however good its ping looks.
    When download was measured too, it takes a share of the upload weight.
    """
    # An SNI qualifies on its upload alone. Requiring a latency reading here
    # would zero out exactly the hosts whose probe timed out on a slow link but
    # whose tunnel turned out to work.
    usable = [r for r in results
              if r['reachable'] and (r.get('upload_mbps') or r['latency_min'])]
    if not usable:
        return results

    has_download = any(r.get('download_mbps') for r in usable)
    # Jitter is only measured in --phased mode; without it that weight has to go
    # somewhere, and upload is what the ranking is actually about.
    has_jitter = any(r.get('jitter') is not None for r in usable)

    w_up, w_down, w_lat, w_jit = 0.65, 0.00, 0.25, 0.10
    if has_download:
        w_up, w_down = 0.45, 0.20
    if not has_jitter:
        w_up += w_jit
        w_jit = 0.0

    max_down = max((r['download_mbps'] or 0) for r in usable) or 1
    max_up = max((r['upload_mbps'] or 0) for r in usable) or 1
    latencies = [r['latency_min'] for r in usable if r['latency_min']]
    min_lat = min(latencies) if latencies else 1
    min_jit = min((r['jitter'] or 0) for r in usable) if has_jitter else 0

    for record in results:
        if record not in usable:
            record['score'] = 0.0
            continue
        down_n = (record['download_mbps'] or 0) / max_down
        up_n = (record['upload_mbps'] or 0) / max_up
        jit_n = 0.0
        if w_jit:
            jit_n = (min_jit + 1) / ((record['jitter'] or 0) + 1)

        # No latency reading for this host: give its share of the weight to
        # upload rather than scoring it as though the link were slow.
        up_w, lat_w = w_up, w_lat
        if not record['latency_min']:
            up_w, lat_w = w_up + w_lat, 0.0
            lat_n = 0.0
        else:
            lat_n = min_lat / record['latency_min']

        record['score'] = round(100 * (up_w * up_n + w_down * down_n +
                                       lat_w * lat_n + w_jit * jit_n), 1)
    return results


# ============================================================================
# SECTION 9: OUTPUT - console, txt, csv, json, html
# ============================================================================

def print_final_table(results):
    ranked = sorted([r for r in results if r['reachable']],
                    key=lambda r: r.get('score', 0), reverse=True)
    # Anything that failed to produce an upload number sinks to the bottom, so a
    # broken measurement never outranks a real one on latency alone.
    ranked.sort(key=lambda r: (r.get('upload_mbps') is None,))
    if not ranked:
        print_warning('No SNI survived the benchmark stage.')
        return ranked

    has_download = any(r.get('download_mbps') for r in ranked)
    has_jitter = any(r.get('jitter') is not None for r in ranked)

    print(f"\n{GREEN}{BOLD}FINAL RANKING{RESET}\n")
    header = (f"{'#':<4}{'SNI':<40}{'Score':>7}{'Upload':>12}"
              f"{'Ping':>8}" + ("{:>9}".format('Jitter') if has_jitter else '')
              + (f"{'Down':>11}" if has_download else ''))
    print(f"{CYAN}{header}{RESET}")
    print(f"{CYAN}{'-' * len(header)}{RESET}")
    for index, record in enumerate(ranked, 1):
        up = f"{record['upload_mbps']:.2f}" if record['upload_mbps'] else '-'
        line = (f"{index:<4}{record['sni']:<40}{record.get('score', 0):>7}"
                f"{up:>12}"
                f"{record['latency_min'] if record['latency_min'] else '-':>7}ms")
        if has_jitter:
            jit = record['jitter'] if record['jitter'] is not None else '-'
            line += f"{jit:>8}ms"
        if has_download:
            down = f"{record['download_mbps']:.2f}" if record['download_mbps'] else '-'
            line += f"{down:>11}"
        print(line)
    print(f"{CYAN}{'-' * len(header)}{RESET}")
    return ranked


def save_outputs(results, stage1, server, outdir='results'):
    """Write txt / csv / json / html reports and the importable link list."""
    results_dir = Path(outdir)
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ranked = sorted([r for r in results if r['reachable']],
                    key=lambda r: r.get('score', 0), reverse=True)

    base = results_dir / f'sni_speedscan_{stamp}'

    # --- plain text summary -------------------------------------------------
    with open(f'{base}.txt', 'w', encoding='utf-8') as handle:
        handle.write('=' * 96 + '\n')
        handle.write('REALITY SNI SPEED SCANNER - RESULTS\n')
        handle.write(f"Date       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        handle.write(f"Server     : {server['server_ip']}:{server['port']}\n")
        handle.write(f"Transport  : {server['transport']}\n")
        handle.write(f"Probed     : {len(stage1)} SNIs\n")
        handle.write(f"Reachable  : {sum(1 for r in stage1 if r['success'])}\n")
        handle.write(f"Benchmarked: {len(results)}\n")
        handle.write('=' * 96 + '\n\n')
        handle.write(f"{'#':<4}{'SNI':<40}{'Score':>7}{'Ping':>9}{'Jitter':>9}"
                     f"{'Down Mbps':>12}{'Up Mbps':>10}\n")
        handle.write('-' * 96 + '\n')
        for index, record in enumerate(ranked, 1):
            handle.write(f"{index:<4}{record['sni']:<40}{record.get('score', 0):>7}"
                         f"{record['latency_min'] if record['latency_min'] else '-':>7}ms"
                         f"{record['jitter'] if record['jitter'] is not None else '-':>7}ms"
                         f"{record['download_mbps'] or 0:>12}{record['upload_mbps'] or 0:>10}\n")
        handle.write('-' * 96 + '\n\nCONFIG LINKS\n' + '=' * 96 + '\n\n')
        for record in ranked:
            handle.write(f"{record['sni']}\n{record['link']}\n\n")

    # --- importable subscription list ---------------------------------------
    with open(f'{base}_links.txt', 'w', encoding='utf-8') as handle:
        for record in ranked:
            handle.write(record['link'] + '\n')

    # --- csv ----------------------------------------------------------------
    with open(f'{base}.csv', 'w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['rank', 'sni', 'score', 'latency_min_ms', 'latency_avg_ms',
                         'jitter_ms', 'download_mbps', 'upload_mbps', 'link'])
        for index, record in enumerate(ranked, 1):
            writer.writerow([index, record['sni'], record.get('score', 0),
                             record['latency_min'], record['latency_avg'],
                             record['jitter'], record['download_mbps'],
                             record['upload_mbps'], record['link']])

    # --- json ---------------------------------------------------------------
    with open(f'{base}.json', 'w', encoding='utf-8') as handle:
        json.dump({
            'generated_at': datetime.now().isoformat(timespec='seconds'),
            'server': {'ip': server['server_ip'], 'port': server['port'],
                       'transport': server['transport']},
            'stage1': stage1,
            'stage2': ranked,
        }, handle, indent=2, ensure_ascii=False)

    # --- html ---------------------------------------------------------------
    write_html_report(f'{base}.html', ranked, stage1, server)

    print_success(f'Report   : {base}.html')
    print_success(f'Summary  : {base}.txt')
    print_success(f'Spreadsheet: {base}.csv')
    print_success(f'Links    : {base}_links.txt')
    return base


def write_html_report(path, ranked, stage1, server):
    """Self-contained sortable HTML report, readable in light and dark mode."""
    has_download = any(r.get('download_mbps') for r in ranked)
    max_down = max([r['download_mbps'] or 0 for r in ranked], default=1) or 1
    max_up = max([r['upload_mbps'] or 0 for r in ranked], default=1) or 1

    rows = []
    for index, record in enumerate(ranked, 1):
        up = record['upload_mbps'] or 0
        down_cell = ''
        if has_download:
            down = record['download_mbps'] or 0
            down_cell = (f'<td><div class="bar dl"><span style="width:'
                         f'{down / max_down * 100:.0f}%"></span></div>{down:.2f} Mbps</td>')
        rows.append(f"""<tr>
<td>{index}</td>
<td class="sni">{record['sni']}</td>
<td><b>{record.get('score', 0)}</b></td>
<td><div class="bar up"><span style="width:{up / max_up * 100:.0f}%"></span></div>{up:.2f} Mbps</td>
<td>{record['latency_min'] if record['latency_min'] else '-'} ms</td>
<td>{record['jitter'] if record['jitter'] is not None else '-'} ms</td>
{down_cell}<td><input class="lnk" readonly value="{record['link']}"></td>
</tr>""")

    reachable = sum(1 for r in stage1 if r['success'])
    html = f"""<title>SNI Speed Scan</title>
<style>
:root {{ --bg:#fff; --fg:#16181d; --muted:#5b6270; --line:#e3e6ec;
        --card:#f7f8fa; --accent:#2563eb; --accent2:#0d9488; }}
:root:not([data-theme="light"]) {{ }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg:#0f1115; --fg:#e6e8ee; --muted:#9aa3b2;
        --line:#252a33; --card:#171a21; --accent:#60a5fa; --accent2:#2dd4bf; }}
}}
:root[data-theme="dark"] {{ --bg:#0f1115; --fg:#e6e8ee; --muted:#9aa3b2;
        --line:#252a33; --card:#171a21; --accent:#60a5fa; --accent2:#2dd4bf; }}
body {{ background:var(--bg); color:var(--fg); font:14px/1.5 system-ui,sans-serif;
        margin:0; padding:28px; }}
h1 {{ font-size:20px; margin:0 0 4px; }}
.meta {{ color:var(--muted); margin-bottom:20px; font-size:13px; }}
.wrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; min-width:900px; }}
th,td {{ padding:9px 12px; text-align:left; border-bottom:1px solid var(--line);
        white-space:nowrap; }}
th {{ background:var(--card); font-weight:600; cursor:pointer; user-select:none;
      position:sticky; top:0; }}
th:hover {{ color:var(--accent); }}
tr:last-child td {{ border-bottom:none; }}
.sni {{ font-family:ui-monospace,monospace; }}
.bar {{ display:inline-block; width:90px; height:6px; background:var(--line);
        border-radius:3px; overflow:hidden; margin-right:8px; vertical-align:middle; }}
.bar span {{ display:block; height:100%; background:var(--accent); }}
.bar.up span {{ background:var(--accent2); }}
.bar.dl span {{ background:var(--accent); }}
.lnk {{ width:230px; font-family:ui-monospace,monospace; font-size:11px;
        background:var(--card); color:var(--muted); border:1px solid var(--line);
        border-radius:6px; padding:4px 6px; }}
</style>
<h1>Reality SNI Speed Scan</h1>
<div class="meta">
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &middot;
server {server['server_ip']}:{server['port']} &middot;
transport {server['transport']} &middot;
{len(stage1)} probed, {reachable} reachable, {len(ranked)} benchmarked
</div>
<div class="wrap"><table id="t">
<thead><tr><th>#</th><th>SNI</th><th>Score</th><th>Upload</th><th>Ping</th>
<th>Jitter</th>{'<th>Download</th>' if has_download else ''}<th>Link</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody></table></div>
<script>
document.querySelectorAll('#t th').forEach(function (th, i) {{
  th.addEventListener('click', function () {{
    var tb = document.querySelector('#t tbody');
    var rows = Array.from(tb.rows);
    var dir = th.dataset.dir === 'asc' ? -1 : 1;
    th.dataset.dir = dir === 1 ? 'asc' : 'desc';
    rows.sort(function (a, b) {{
      var x = a.cells[i].innerText.trim(), y = b.cells[i].innerText.trim();
      var nx = parseFloat(x), ny = parseFloat(y);
      if (!isNaN(nx) && !isNaN(ny)) return (nx - ny) * dir;
      return x.localeCompare(y) * dir;
    }});
    rows.forEach(function (r) {{ tb.appendChild(r); }});
  }});
}});
</script>"""
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(html)


# ============================================================================
# SECTION 10: SERVER API
# ============================================================================

def server_health(server_ip, api_port, timeout=10):
    """Check the scanner API and explain exactly why it is unreachable."""
    url = f'http://{server_ip}:{api_port}/health'
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True
        print_error(f'API answered with HTTP {response.status_code} instead of 200.')
        print_info(f'Something is listening on {server_ip}:{api_port}, but it is '
                   f'not the scanner API.')
        return False
    except requests.exceptions.ConnectTimeout:
        print_error(f'Timed out connecting to {server_ip}:{api_port}.')
        print_info('The port is filtered. Open it in the VPS firewall and in your '
                   "provider's external firewall / security group.")
    except requests.exceptions.ConnectionError as exc:
        if 'refused' in str(exc).lower():
            print_error(f'Connection refused by {server_ip}:{api_port}.')
            print_info('The host is up but nothing is listening on that port. '
                       'Start the server first:')
            print_info('    sudo python3 server-sniScanner.py')
            print_info('and use the API port it prints - it shifts to a free port '
                       'when the one you asked for is taken.')
        else:
            print_error(f'Cannot reach {server_ip}:{api_port} - {exc.__class__.__name__}')
            print_info('Check that the IP is right and the host is reachable.')
    except Exception as exc:
        print_error(f'Health check failed: {type(exc).__name__}: {exc}')
    return False


def send_config_to_server(server_ip, sni_list, transport, batch_size, api_port):
    try:
        response = requests.post(
            f'http://{server_ip}:{api_port}/api/send_config',
            json={'sni_list': sni_list, 'transport': transport, 'batch_size': batch_size},
            timeout=30)
        if response.status_code == 200:
            return response.json()
        print_error(f'Server returned {response.status_code}')
    except Exception as exc:
        print_error(f'Cannot reach server API: {exc}')
    return None


def apply_server_batch(server_ip, sni_batch, transport, batch_index, total_batches, api_port):
    try:
        response = requests.post(
            f'http://{server_ip}:{api_port}/api/apply_batch',
            json={'sni_batch': sni_batch, 'transport': transport,
                  'batch_index': batch_index, 'total_batches': total_batches},
            timeout=60)
        return response.status_code == 200
    except Exception:
        return False


def fetch_port_map(server_ip, api_port):
    """Read the live SNI -> port map without touching the server config."""
    try:
        response = requests.get(f'http://{server_ip}:{api_port}/api/portmap', timeout=30)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            print_error('Server has no /api/portmap. Update server-sniScanner.py.')
        else:
            print_error(f'Server returned {response.status_code} for portmap')
    except Exception as exc:
        print_error(f'Cannot fetch port map: {exc}')
    return None


def apply_server_multi(server_ip, sni_batch, transport, base_port,
                       chunk_index, total_chunks, api_port):
    """Ask the server for one dedicated inbound per SNI. Returns {sni: port}."""
    try:
        response = requests.post(
            f'http://{server_ip}:{api_port}/api/apply_multi',
            json={'sni_batch': sni_batch, 'transport': transport,
                  'base_port': base_port, 'chunk_index': chunk_index,
                  'total_chunks': total_chunks},
            timeout=120)
        if response.status_code == 200:
            return response.json().get('port_map', {})
        if response.status_code == 404:
            print_error('Server does not support /api/apply_multi. '
                        'Update server-sniScanner.py, or run the client with --legacy.')
        else:
            print_error(f'Server returned {response.status_code} for apply_multi')
    except Exception as exc:
        print_error(f'apply_multi failed: {exc}')
    return None


# ============================================================================
# SECTION 11: SNI INPUT
# ============================================================================

DEFAULT_SNIS = [
    'www.speedtest.net', 'www.yahoo.com', 'www.bing.com', 'www.icloud.com',
    'dl.google.com', 'www.amazon.com', 'aws.amazon.com', 'www.samsung.com',
    'www.microsoft.com', 'gateway.icloud.com', 'cdn.jsdelivr.net',
    'www.lovelive-anime.jp', 'python.org', 'www.wikipedia.org',
]


def load_sni_list(args):
    """Resolve the SNI list from --sni-file, --sni, or the built-in defaults."""
    if args.sni_file:
        path = Path(args.sni_file)
        if not path.exists():
            print_error(f'SNI file not found: {path}')
            return []
        entries = []
        for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = line.strip().lower()
            if not line or line.startswith('#'):
                continue
            line = line.replace('https://', '').replace('http://', '').split('/')[0]
            if '.' in line:
                entries.append(line)
        # Deduplicate while preserving order.
        entries = list(dict.fromkeys(entries))
        if args.shuffle:
            random.shuffle(entries)
        if args.limit:
            entries = entries[:args.limit]
        return entries

    if args.sni:
        return [s.strip() for s in args.sni.split(',') if s.strip()]

    return list(DEFAULT_SNIS)


# ============================================================================
# SECTION 12: SIGNAL HANDLING
# ============================================================================

def emergency_save():
    """Persist whatever has been measured so far."""
    if not _stage1_results and not _stage2_results:
        return
    server = _scan_state['server']
    if server is None:
        return
    print_info('Saving partial results...')
    scored = score_results(list(_stage2_results))
    try:
        save_outputs(scored, list(_stage1_results), server)
    except Exception as exc:
        print_error(f'Could not save partial results: {exc}')


def signal_handler(signum, frame):
    print()
    print_warning('Interrupted.')
    if not _scan_state['completed']:
        emergency_save()
    kill_all_xray()
    sys.exit(130)


# ============================================================================
# SECTION 13: MAIN
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Reality SNI scanner with download/upload benchmarking.')
    parser.add_argument('--server', required=True, help='Server IP running the scanner API')
    parser.add_argument('--api-port', type=int, default=8080, help='Server API port')
    parser.add_argument('--transport', default='tcp',
                        choices=list(URI_TYPE.keys()), help='Transport to test')
    parser.add_argument('--sni-file', help='File with one SNI per line')
    parser.add_argument('--sni', help='Comma separated SNI list')
    parser.add_argument('--limit', type=int, help='Only test the first N SNIs from the file')
    parser.add_argument('--shuffle', action='store_true', help='Shuffle the SNI file first')
    parser.add_argument('--batch-size', type=int, default=80,
                        help='SNIs per server config (one Xray restart each)')
    parser.add_argument('--base-port', type=int, default=30000,
                        help='First port of the dedicated-inbound range on the server')
    parser.add_argument('--legacy', action='store_true',
                        help='Use the old shared-target batch mode. Faster to set up '
                             '(single port) but reports healthy SNIs as broken whenever '
                             "the batch target's server rejects their name.")
    parser.add_argument('--workers', type=int, default=8,
                        help='Parallel workers for stage 1 (stage 2 is always serial)')
    parser.add_argument('--top', type=int, default=0,
                        help='How many stage-1 survivors to benchmark. '
                             '0 (the default) benchmarks every reachable SNI')
    parser.add_argument('--upload-mb', type=int, default=16,
                        help='Upload sample ceiling per SNI; --upload-seconds '
                             'usually stops the transfer well before this')
    parser.add_argument('--upload-seconds', type=float, default=10.0,
                        help='Seconds cap per upload measurement')
    parser.add_argument('--use-existing', action='store_true',
                        help='Scan the config already live on the server '
                             'instead of applying one. Required when several '
                             'machines scan at once: applying restarts Xray and '
                             'replaces everyone else\'s inbounds')
    parser.add_argument('--probe-gate', action='store_true',
                        help='Drop an SNI when its probe fails, instead of '
                             'upload-testing it anyway. The probe is an HTTP '
                             'request to speed.cloudflare.com through the '
                             'tunnel, so on a slow link it can fail while the '
                             'tunnel works - which is why gating is off')
    parser.add_argument('--probe-timeout', type=float, default=5.0,
                        help='Seconds to wait for a tunnel to connect before '
                             'calling the attempt failed. Raise it on a slow '
                             'or lossy link')
    parser.add_argument('--phased', action='store_true',
                        help='Probe everything first, then upload-test everything. '
                             'Slower to first result, but latency is measured on an '
                             'idle link instead of under upload load')
    parser.add_argument('--with-download', action='store_true',
                        help='Also measure download. Off by default: shaping '
                             'shows on the upload path first')
    parser.add_argument('--download-mb', type=int, default=8, help='Initial download sample size')
    parser.add_argument('--max-download-mb', type=int, default=48,
                        help='Larger sample used when the link drains the first one fast')
    parser.add_argument('--time-cap', type=float, default=8.0,
                        help='Seconds cap per download measurement')
    parser.add_argument('--ping-samples', type=int, default=5,
                        help='Latency samples per SNI in stage 2')
    parser.add_argument('--skip-speed', action='store_true',
                        help='Stage 1 only, no throughput benchmark')
    return parser.parse_args()


def print_eta(count, args, unknown_reachable=False):
    """Say up front how long the serial upload pass will take."""
    per_sni = args.upload_seconds + 2.0          # tunnel setup and teardown
    if args.phased:
        per_sni += (args.ping_samples + 1) * 0.6  # latency sampling
    if args.with_download:
        per_sni += args.time_cap
    minutes = count * per_sni / 60
    qualifier = 'at most ' if unknown_reachable else ''
    print_info(f'{qualifier}{count} SNIs x ~{per_sni:.0f}s = {qualifier}'
               f'{minutes:.0f} minutes. Ctrl+C saves what is done so far.')


def finish_latency_only(reachable, server):
    """--skip-speed: emit reports built from the probe results alone."""
    latency_only = [{
        'sni': r['sni'], 'link': r['link'], 'remote_port': r.get('remote_port'),
        'reachable': True, 'latency_min': r['latency'], 'latency_avg': r['latency'],
        'jitter': None, 'download_mbps': None, 'upload_mbps': None, 'error': None,
    } for r in reachable]
    score_results(latency_only)
    _scan_state['completed'] = True
    print_final_table(latency_only)
    save_outputs(latency_only, _stage1_results, server)
    kill_all_xray()
    return 0


def main():
    print_banner()
    args = parse_args()
    signal.signal(signal.SIGINT, signal_handler)

    global CONNECT_TIMEOUT
    CONNECT_TIMEOUT = args.probe_timeout

    if not get_xray_path():
        print_error('xray executable not found. Install Xray-core first.')
        return 1

    # requests cannot open a socks5h:// proxy without PySocks, and the failure
    # surfaces as a per-SNI error that looks like a dead SNI.
    try:
        import socks  # noqa: F401
    except ImportError:
        print_error('PySocks is missing. Install it with:  pip install PySocks')
        return 1

    sni_list = load_sni_list(args)
    if not sni_list:
        print_error('Empty SNI list.')
        return 1

    print_info(f'Connecting to scanner API at {args.server}:{args.api_port} ...')
    if not server_health(args.server, args.api_port):
        print_error('Server health check failed.')
        return 1
    print_success('Server reachable')

    existing_map = None
    if args.use_existing:
        payload = fetch_port_map(args.server, args.api_port)
        if not payload or not payload.get('port_map'):
            print_error('No config is live on the server. Have one machine run '
                        'without --use-existing first to set the inbounds up.')
            return 1
        existing_map = payload['port_map']
        # Only scan SNIs the live config actually serves.
        wanted = [s for s in sni_list if s in existing_map]
        missing = len(sni_list) - len(wanted)
        if not wanted:
            print_error('None of your SNIs are in the live config. Either use '
                        'the same list as the machine that set it up, or drop '
                        '--sni-file to scan everything it serves.')
            return 1
        if missing:
            print_warning(f'{missing} of your SNIs are not in the live config '
                          f'and will be skipped.')
        sni_list = wanted
        config = {
            'server_ip': payload['server_ip'], 'port': 0,
            'public_key': payload['public_key'],
            'short_id': payload['short_id'],
            'server_uuid': payload['server_uuid'],
            'batches': [sni_list], 'total_batches': 1,
        }
        print_success(f'Reusing the live config: {len(existing_map)} inbounds, '
                      f'scanning {len(sni_list)} of them')
    else:
        config = send_config_to_server(args.server, sni_list, args.transport,
                                       args.batch_size, args.api_port)
        if not config:
            return 1

    server = {
        'server_ip': config['server_ip'],
        'port': config['port'],
        'public_key': config['public_key'],
        'short_id': config['short_id'],
        'server_uuid': config['server_uuid'],
        'transport': args.transport,
    }
    _scan_state['server'] = server

    print_success(f"Reality endpoint {server['server_ip']}:{server['port']} "
                  f"({args.transport})")
    print_info(f"{len(sni_list)} SNIs in {config['total_batches']} batch(es), "
               f"{args.workers} workers")

    if args.legacy:
        print_warning('Legacy shared-target mode produces unreliable verdicts:')
        print_warning('  - SNIs the batch target rejects are reported broken though healthy')
        print_warning('  - SNIs that do not even resolve are reported working')
        print_warning('Use it only when the dedicated port range cannot be opened.')

    batches = config['batches']

    def apply_chunk(chunk, index, count):
        """Put one chunk of SNIs live on the server. Returns {sni: port} or None.

        With --use-existing this does nothing at all. That is the whole point:
        an apply restarts Xray, which drops every other machine's inbounds and
        cuts their transfers mid-flight.
        """
        if existing_map is not None:
            return {s: existing_map[s] for s in chunk}
        if args.legacy:
            ok = apply_server_batch(args.server, chunk, args.transport,
                                    index, count, args.api_port)
            return {} if ok else None
        return apply_server_multi(args.server, chunk, args.transport,
                                  args.base_port, index, count, args.api_port)

    results = []

    if args.phased:
        # ---- two separate passes: every probe first, then every upload ----
        print_step('STAGE 1 - reachability and latency probe')
        for index, batch in enumerate(batches):
            print_info(f'Batch {index + 1}/{len(batches)} ({len(batch)} SNIs)...')
            port_map = apply_chunk(batch, index, len(batches))
            if port_map is None:
                print_error(f'Server failed to apply batch {index + 1}, skipping')
                continue
            time.sleep(3)
            run_stage1(server, batch, index, args.workers, port_map)

        reachable = [r for r in _stage1_results if r['success']]
        print_info(f'\nStage 1 done: {len(reachable)}/{len(_stage1_results)} reachable')
        if not reachable:
            print_warning('No reachable SNI. Check the server firewall, the '
                          'transport, or try a different SNI list.')
            _scan_state['completed'] = True
            kill_all_xray()
            return 0
        if args.skip_speed:
            return finish_latency_only(reachable, server)

        reachable.sort(key=lambda r: r['latency'])
        finalists = [r['sni'] for r in reachable]
        if args.top and args.top < len(finalists):
            finalists = finalists[:args.top]

        print_step(f'STAGE 2 - upload benchmark, {len(finalists)} SNIs (serial)')
        print_eta(len(finalists), args)
        chunks = [finalists[i:i + args.batch_size]
                  for i in range(0, len(finalists), args.batch_size)]
        for index, chunk in enumerate(chunks):
            if len(chunks) > 1:
                print_info(f'Chunk {index + 1}/{len(chunks)} ({len(chunk)} SNIs)...')
            port_map = apply_chunk(chunk, index, len(chunks))
            if port_map is None:
                print_error(f'Server failed to apply chunk {index + 1}, skipping')
                continue
            time.sleep(3)
            results.extend(run_stage2(server, chunk, args, port_map))

    else:
        # ---- pipelined: each successful probe uploads immediately ----
        mode = 'shared-target (legacy)' if args.legacy else 'dedicated inbound per SNI'
        if args.skip_speed:
            print_step(f'SCAN - reachability and latency only [{mode}]')
        else:
            print_step(f'SCAN - ping then upload, per SNI [{mode}]')
            print_info('Probes run in parallel; upload tests run one at a time '
                       'so they do not compete for your uplink.')
            print_eta(len(sni_list), args, unknown_reachable=True)

        for index, batch in enumerate(batches):
            print_info(f'Batch {index + 1}/{len(batches)} ({len(batch)} SNIs) - '
                       f'applying server config...')
            port_map = apply_chunk(batch, index, len(batches))
            if port_map is None:
                print_error(f'Server failed to apply batch {index + 1}, skipping')
                continue
            if existing_map is None:
                time.sleep(3)
            if args.skip_speed:
                run_stage1(server, batch, index, args.workers, port_map)
            else:
                results.extend(run_pipelined(server, batch, index, args, port_map))

        reachable = [r for r in _stage1_results if r['success']]
        print_info(f'\nProbed {len(_stage1_results)}, reachable {len(reachable)}, '
                   f'benchmarked {len(results)}')
        if args.skip_speed:
            return finish_latency_only(reachable, server)

    _scan_state['completed'] = True

    score_results(results)
    print_final_table(results)
    save_outputs(results, _stage1_results, server)

    kill_all_xray()
    print(f"\n{GREEN}{BOLD}Done.{RESET}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
