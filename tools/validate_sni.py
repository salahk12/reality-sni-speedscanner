#!/usr/bin/env python3
"""
Validate SNI candidates for Reality use, from the server that will host them.

A hostname is only usable as a Reality target if the server can complete a
TLS 1.3 handshake against it with that SNI, negotiate HTTP/2, and get back a
certificate that actually covers the name. Anything less and the handshake
relay breaks, which is exactly the failure that silently discards good SNIs.

Usage:
    python3 validate_sni.py candidates.txt > verified.txt
    python3 validate_sni.py candidates.txt --json report.json --workers 60
"""

import sys
import ssl
import json
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed


def check(host, timeout=6.0):
    """Return a dict describing how usable this host is as a Reality target."""
    result = {
        'host': host, 'ok': False, 'tls13': False, 'h2': False,
        'cert_match': False, 'handshake_ms': None, 'issuer': None,
        'peer_ip': None, 'error': None,
    }

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_3   # Reality requires 1.3
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_default_certs()
    try:
        context.set_alpn_protocols(['h2', 'http/1.1'])
    except NotImplementedError:
        pass

    import time
    started = time.time()
    try:
        with socket.create_connection((host, 443), timeout=timeout) as raw:
            raw.settimeout(timeout)
            # Recording where the name actually lands is what makes wildcard
            # DNS visible later: a dozen generated subdomains of one SaaS apex
            # all resolve to the same edge and are not the independent targets
            # their names suggest.
            result['peer_ip'] = raw.getpeername()[0]
            with context.wrap_socket(raw, server_hostname=host) as tls:
                result['handshake_ms'] = int((time.time() - started) * 1000)
                result['tls13'] = tls.version() == 'TLSv1.3'
                result['h2'] = tls.selected_alpn_protocol() == 'h2'
                # check_hostname=True means we only get here on a name match
                result['cert_match'] = True
                cert = tls.getpeercert() or {}
                issuer = dict(x[0] for x in cert.get('issuer', ()))
                result['issuer'] = issuer.get('organizationName')
    except ssl.SSLCertVerificationError as exc:
        result['error'] = f'cert: {exc.verify_message or exc}'
        return result
    except ssl.SSLError as exc:
        result['error'] = f'tls: {exc.reason or exc}'
        return result
    except socket.timeout:
        result['error'] = 'timeout'
        return result
    except socket.gaierror:
        result['error'] = 'dns'
        return result
    except OSError as exc:
        result['error'] = f'net: {exc.strerror or exc}'
        return result
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}'
        return result

    result['ok'] = result['tls13'] and result['h2'] and result['cert_match']
    if not result['ok']:
        missing = []
        if not result['tls13']:
            missing.append('no TLS1.3')
        if not result['h2']:
            missing.append('no h2')
        result['error'] = ', '.join(missing)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('--workers', type=int, default=60)
    parser.add_argument('--timeout', type=float, default=6.0)
    parser.add_argument('--json', help='write the full report here')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    hosts = []
    seen = set()
    with open(args.infile, encoding='utf-8', errors='ignore') as handle:
        for line in handle:
            name = line.strip().lower()
            if name and not name.startswith('#') and '.' in name and name not in seen:
                seen.add(name)
                hosts.append(name)

    if not args.quiet:
        print(f'checking {len(hosts)} hosts with {args.workers} workers...',
              file=sys.stderr)

    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check, h, args.timeout): h for h in hosts}
        for future in as_completed(futures):
            results.append(future.result())
            done += 1
            if not args.quiet and done % 100 == 0:
                good = sum(1 for r in results if r['ok'])
                print(f'  {done}/{len(hosts)}  passing: {good}', file=sys.stderr)

    passing = [r for r in results if r['ok']]
    # Fastest handshake first: a nearby target keeps the Reality relay cheap.
    passing.sort(key=lambda r: r['handshake_ms'])

    for record in passing:
        print(record['host'])

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as handle:
            json.dump(results, handle, indent=1)

    if not args.quiet:
        failed = len(results) - len(passing)
        print(f'\npassed: {len(passing)}   failed: {failed}', file=sys.stderr)
        reasons = {}
        for record in results:
            if not record['ok']:
                key = (record['error'] or 'unknown').split(':')[0][:28]
                reasons[key] = reasons.get(key, 0) + 1
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1])[:10]:
            print(f'  {count:>5}  {reason}', file=sys.stderr)


if __name__ == '__main__':
    main()
