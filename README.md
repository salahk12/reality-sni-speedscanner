# Reality SNI Speed Scanner

**[فارسی](README.fa.md)** · English

Finds Reality SNIs that are still **fast to upload through** from a censored
network — not just ones that answer a ping.

Traffic shapers work per SNI, and upload is what they squeeze first: an SNI can
hold full download speed while its upload collapses. Latency won't show you
that, so this moves real bytes. Two SNIs on the same server and port can differ
tenfold in upload throughput.

A fork of [Master_Reality_SNI_Scanner](https://github.com/AminDaProgrammer/Master_Reality_SNI_Scanner)
— see [CHANGELOG.md](CHANGELOG.md) for what changed and why.

---

## Install the server (VPS abroad)

```bash
curl -fsSL https://raw.githubusercontent.com/salahk12/reality-sni-speedscanner/main/install-server.sh | sudo bash
```

Installs Xray-core and dependencies, reserves the inbound port range, opens the
firewall, and runs the API as a systemd service. Prints the client command when
done.

Passing options through the pipe needs `-s --`:

```bash
curl -fsSL .../install-server.sh | sudo bash -s -- --api-port 9090 --count 500
```

| Option | |
| --- | --- |
| `--api-port N` | API port (default 8080) |
| `--base-port N` | First inbound port (default 30000) |
| `--count N` | How many inbound ports (default 1000) |
| `--force` | Run anyway on a host with a proxy panel |

> **Use a clean VPS.** The scanner rewrites the Xray config and restarts the
> service, which disturbs an x-ui / 3x-ui / Marzban / Hiddify panel on the same
> box. The installer refuses unless you pass `--force`.

## Run the scan (your machine)

Needs Python 3, `xray` (or `xray.exe` beside the script), `requests`, `PySocks`:

```bash
pip install requests PySocks
# Ubuntu 24 / Debian 12 (PEP 668): sudo apt install python3-requests python3-socks
```

```bash
curl http://<SERVER_IP>:8080/health      # expects {"status": "ok", ...}

python client-speedScanner.py --server <SERVER_IP> --api-port 8080 \
    --sni-file sni-1000.txt --limit 300 --workers 16 --upload-seconds 5
```

Results go to `results/` — a sortable `.html` report plus `.csv`, `.json`,
`.txt`, and `_links.txt` with one importable `vless://` per line.

---

## The SNI lists

Every hostname was verified **from a server abroad** to do TLS 1.3, negotiate
HTTP/2, and present a certificate for its own name — what a Reality target must
do.

| File | |
| --- | --- |
| `sni-1000.txt` | 1000 foreign hostnames, 764 organisations |
| `sni-1000-v2.txt` | 1000 more, no overlap with the first |
| `sni-1000-ir.txt` | 1000 domestic Iranian hostnames |

The foreign lists are ordered **infrastructure-first** (`api.`, `cdn.`, `edge.`,
`dl.`, `static.` before front pages), because a brand's homepage is the first
name a shaper learns while the same company's telemetry endpoints keep working.
No `www.` homepage appears in the first 300, so `--limit 300` gives you the
quiet endpoints only.

The Iranian list is ordered the other way — big recognisable sites first —
since a domestic SNI should look like ordinary local traffic. **Expect it to be
flaky:** eight foreign SNIs came back 8/8 on four consecutive runs while eight
Iranian ones gave 3/8, 7/8, 5/8, 6/8. Run a domestic scan a few times and keep
what passes consistently.

Build your own (run the validator **on the server that will host the
inbounds**):

```bash
python3 tools/build_sni_candidates.py > candidates.txt
python3 tools/validate_sni.py candidates.txt --json report.json > verified.txt
python3 tools/rank_sni.py report.json --limit 1000 --pin your.known.good.host
```

## Scanning from several machines

The server keeps one Xray config and restarts it on every change, so a second
client applying its own config wipes the first one's inbounds. Three clients at
once:

```
without --use-existing   0/40   38/40   39/40
with    --use-existing  39/40   34/40   40/40
```

Publish the inbounds once, then reuse them everywhere:

```bash
# once, from any machine
python client-speedScanner.py --server <IP> --api-port 8080 \
    --sni-file sni-1000.txt --batch-size 1000 --skip-speed

# then on every machine, in parallel
python client-speedScanner.py --server <IP> --api-port 8080 \
    --sni-file sni-1000.txt --use-existing --workers 16 --upload-seconds 5
```

1000 inbounds cost ~550 MB RAM on the server; publish 300–500 if memory is tight.

---

## Options

| Flag | |
| --- | --- |
| `--sni-file FILE` | List to scan, one hostname per line |
| `--limit N` | First N of the file. Lists are pre-ranked, so this is the best N |
| `--workers N` | Parallel probes (default 8). Upload stays serial, so this doesn't shorten it |
| `--upload-seconds N` | Time budget per upload (default 10) |
| `--upload-mb N` | Sample ceiling per SNI (default 16). Raise if your uplink is >13 Mbps and numbers look noisy |
| `--probe-timeout N` | Tunnel connect timeout (default 5). Raise on a slow link |
| `--use-existing` | Scan the server's live config, apply nothing. Needed for concurrent clients |
| `--skip-speed` | Reachability and latency only |
| `--with-download` | Also measure download (off by default) |
| `--phased` | Probe all, then upload all. Cleaner latency and jitter, slower to first result |
| `--probe-gate` | Drop an SNI when its probe fails instead of upload-testing it anyway |
| `--top N` | Benchmark only the N fastest. Default 0 = all |
| `--transport` | tcp, websocket, grpc, http2, xhttp, quic, splithttp |

Score: `0.75 × upload + 0.25 × latency` by default. Normalised against the best
value in the same run, so it ranks within one scan and isn't comparable across
scans.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| `/health` refused | Service down. `systemctl status sniscanner`, `tail /var/log/sniscanner.log` |
| `/health` times out | Port filtered. Open it in the VPS *and* provider firewall — the inbound range too, not just the API port |
| Everything fails at stage 1 | Inbound range unreachable. Test one: `curl -v telnet://<IP>:30000` |
| API on an unexpected port | The server shifts to the next free port; it's printed at startup and in the log |
| Every SNI looks dead | PySocks missing — `requests` can't open a SOCKS proxy without it |
| Upload swings between runs | Uplink fast enough that `--upload-mb` ends the sample inside TCP slow start. Raise it |
| A known-good SNI reported failing | The probe is an HTTP request *through the tunnel*, not a ping, so it times out on slow links. Not a verdict — the SNI still gets upload-tested. Raise `--probe-timeout` |

---

Upstream ships no licence file, so the original code remains under its author's
copyright. Published here with their work attributed and linked.
