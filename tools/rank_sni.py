#!/usr/bin/env python3
"""
Rank verified SNI hosts into a final list.

Two things decide the order:

1. Handshake time measured from the server that will use them. A nearby target
   keeps the Reality relay cheap, and a target that is slow to greet the server
   makes every new connection slow.

2. Whether the hostname looks like infrastructure. Names such as api, cdn,
   edge, dl, static and storage come before front-page names, which are the
   first thing a traffic shaper learns to recognise. This is the primary sort:
   a quiet endpoint at 40 ms beats a marketing homepage at 20 ms.

A per-organisation cap keeps one company from dominating the list, so a single
provider being shaped cannot take the whole list down with it.

Usage:
    python3 rank_sni.py validation.json validation2.json --limit 1000 > sni.txt
"""

import json
import argparse
from collections import defaultdict

# Suffixes that need three labels to identify the organisation.
MULTI_SUFFIXES = {
    'co.uk', 'ac.uk', 'org.uk', 'gov.uk', 'co.jp', 'ac.jp', 'or.jp', 'ne.jp',
    'co.kr', 'ac.kr', 'com.au', 'net.au', 'org.au', 'edu.au', 'gov.au',
    'com.br', 'com.mx', 'com.ar', 'co.nz', 'com.sg', 'com.hk', 'com.tw',
    'co.in', 'com.cn', 'com.tr', 'co.za', 'com.es', 'co.il', 'com.pl',
}

INFRA_HINTS = (
    'api', 'cdn', 'edge', 'static', 'assets', 'storage', 'dl', 'download',
    'media', 'img', 'images', 'files', 'content', 'update', 'updates',
    'repo', 'mirror', 'registry', 'pkg', 'packages', 'archive', 'gateway',
    'ingest', 'telemetry', 'config', 'settings', 'fota', 'swcdn', 'mzstatic',
)


def registrable(host):
    """Approximate eTLD+1, good enough for grouping by organisation."""
    parts = host.split('.')
    if len(parts) < 2:
        return host
    if len(parts) >= 3 and '.'.join(parts[-2:]) in MULTI_SUFFIXES:
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:])


def subnet(record):
    """The /24 a host landed on, or its name when no IP was recorded."""
    ip = record.get('peer_ip')
    if not ip or ':' in ip:            # no data, or IPv6: do not group
        return f"host:{record['host']}"
    return '.'.join(ip.split('.')[:3])


def infra_score(host):
    """0 for infrastructure-looking names, 1 for front-page names.

    Lower sorts first. A hostname with more labels is already a sign of an
    internal endpoint rather than a marketing domain.
    """
    labels = host.split('.')
    head = labels[0]
    if head in ('www', ''):
        return 1
    if any(hint in head for hint in INFRA_HINTS):
        return 0
    return 0 if len(labels) >= 3 else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('reports', nargs='+', help='validation JSON reports')
    parser.add_argument('--limit', type=int, default=1000)
    parser.add_argument('--per-org', type=int, default=6,
                        help='Max hostnames from one organisation')
    parser.add_argument('--pin', default='',
                        help='Comma separated hosts to place first regardless '
                             'of the per-organisation cap. Use this for SNIs you '
                             'have already proven in the field - measured '
                             'evidence outranks the heuristic')
    parser.add_argument('--exclude', action='append', default=[],
                        help='File of hostnames to leave out. Repeatable. Use '
                             'this to build a second list that shares nothing '
                             'with the first')
    parser.add_argument('--per-subnet', type=int, default=2,
                        help='Max hostnames landing on one /24. Wildcard DNS '
                             'makes many generated subdomains resolve to the '
                             'same edge, and names that share an edge share its '
                             'fate')
    parser.add_argument('--prefer', action='append', default=[],
                        help='File of hostnames to rank ahead of everything '
                             'else. Repeatable')
    parser.add_argument('--no-infra-bias', action='store_true',
                        help='Do not push api/cdn/static names ahead of front '
                             'pages. Right for a domestic list, where the goal '
                             'is to look like ordinary local traffic and a well '
                             'known homepage does that better than an obscure '
                             'endpoint')
    parser.add_argument('--stats', action='store_true')
    args = parser.parse_args()

    excluded = set()
    for path in args.exclude:
        with open(path, encoding='utf-8') as handle:
            for line in handle:
                name = line.strip().lower()
                if name and not name.startswith('#'):
                    excluded.add(name)

    records = {}
    for path in args.reports:
        with open(path, encoding='utf-8') as handle:
            for record in json.load(handle):
                if (record.get('ok') and record['host'] not in records
                        and record['host'] not in excluded):
                    records[record['host']] = record

    # Infrastructure names first, fastest handshake first within each tier.
    # Round-robin across organisations was tried and is wrong here: it fills the
    # head of the list with one front-page domain per company, which is exactly
    # the shape of hostname that gets shaped first.
    preferred = set()
    for path in args.prefer:
        with open(path, encoding='utf-8') as handle:
            for line in handle:
                name = line.strip().lower()
                if name and not name.startswith('#'):
                    preferred.add(name)

    def sort_key(record):
        tier = 0 if record['host'] in preferred else 1
        bias = 0 if args.no_infra_bias else infra_score(record['host'])
        return (tier, bias, record['handshake_ms'])

    everything = sorted(records.values(), key=sort_key)

    # A per-organisation cap keeps diversity without disturbing that order, so
    # no single company can dominate the list and take it down with them.
    pinned = [h.strip().lower() for h in args.pin.split(',') if h.strip()]
    ranked = []
    per_org = defaultdict(int)
    per_net = defaultdict(int)
    seen = set()
    for host in pinned:
        if host in records:
            ranked.append(records[host])
            per_org[registrable(host)] += 1
            per_net[subnet(records[host])] += 1
            seen.add(host)
        else:
            import sys
            print(f'pin skipped, not verified: {host}', file=sys.stderr)

    overflow = []
    for record in everything:
        if record['host'] in seen:
            continue
        org = registrable(record['host'])
        net = subnet(record)
        if per_org[org] < args.per_org and per_net[net] < args.per_subnet:
            per_org[org] += 1
            per_net[net] += 1
            ranked.append(record)
        else:
            overflow.append(record)
        if len(ranked) >= args.limit:
            break

    # If the cap left us short of the target, top up from what it held back.
    for record in overflow:
        if len(ranked) >= args.limit:
            break
        ranked.append(record)

    for record in ranked:
        print(record['host'])

    if args.stats:
        import sys
        print(f'\nverified hosts : {len(records)}', file=sys.stderr)
        print(f'organisations  : {len(per_org)}', file=sys.stderr)
        print(f'distinct /24s  : {len(per_net)}', file=sys.stderr)
        print(f'emitted        : {len(ranked)}', file=sys.stderr)
        top = [r['host'] for r in ranked[:20]]
        print(f'first 20 span  : {len({registrable(h) for h in top})} orgs',
              file=sys.stderr)


if __name__ == '__main__':
    main()
