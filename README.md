# Reality SNI Speed Scanner

**[فارسی](README.fa.md)** · English

Find Reality SNIs that are still **fast to upload through** from a censored
network — not just ones that answer a ping.

> A fork of [AminDaProgrammer/Master_Reality_SNI_Scanner](https://github.com/AminDaProgrammer/Master_Reality_SNI_Scanner),
> whose server/client design this builds on. The upstream README is kept here as
> [README-upstream.md](README-upstream.md).

---

## Why

The SNI only rides in the TLS handshake, so it is tempting to assume every SNI
performs the same. It does not. Traffic shapers work per SNI, and the **upload**
path is what they squeeze first: an SNI can hold full download speed while its
upload collapses to a trickle. Latency will not show you this. You have to move
real bytes.

Two SNIs on the same server, same port, same protocol, measured minutes apart,
can differ by an order of magnitude in upload throughput. This tool finds which
ones are still good, today, on *your* connection.

---

## How it works

```
   your PC (censored network)                 VPS abroad (e.g. Germany)
   ┌───────────────────────┐                  ┌──────────────────────────┐
   │ client-speedScanner   │──── API ────────▶│ server-sniScanner        │
   │                       │                  │  one Reality inbound     │
   │  probe  ──┐           │                  │  per SNI, own port,      │
   │           ├─ tunnel ──┼─────────────────▶│  own matching target     │
   │  upload ──┘           │                  └──────────────────────────┘
   └───────────────────────┘                              │
              │                                           ▼
              └──────── measures Mbps ──────────▶ speed.cloudflare.com
```

The server builds one Reality inbound per SNI. The client opens a tunnel through
each one and measures how fast it can upload. Probes run in parallel and feed a
single serial uploader, so the uplink is never shared between two measurements
yet results start arriving within seconds.

---

## Quick start

### 1. On the VPS abroad

```bash
git clone https://github.com/salahk12/reality-sni-speedscanner.git
cd reality-sni-speedscanner
sudo bash install-server.sh
```

That installs Xray-core and the Python dependencies, reserves the inbound port
range, opens the firewall, and runs the API as a systemd service so it survives
a reboot. It prints the address and the exact client command when it finishes.

> **Use a clean VPS.** The scanner rewrites the Xray config and restarts the
> service. On a box already running x-ui, 3x-ui, Marzban or Hiddify, that
> interferes with the panel — the installer refuses to run there unless you pass
> `--force`.

Options if the defaults clash with something:

```bash
sudo bash install-server.sh --api-port 9090 --base-port 40000 --count 500
```

### 2. On your own machine

Needs Python 3, `xray` (or `xray.exe` next to the script), plus `requests`
and `PySocks`:

```bash
pip install requests PySocks

# Ubuntu 24 / Debian 12 refuse that (PEP 668). Use the distro packages:
sudo apt install python3-requests python3-socks
```

Check you can reach the server before scanning:

```bash
curl http://<SERVER_IP>:8080/health      # expects {"status": "ok", ...}
```

Then scan:

```bash
python client-speedScanner.py --server <SERVER_IP> --api-port 8080 \
    --sni-file sni-1000.txt --limit 300 --workers 16 --upload-seconds 5
```

Results land in `results/` as a sortable `.html` report, plus `.csv`, `.json`,
`.txt`, and `_links.txt` with one importable `vless://` per line.

---

## The SNI lists

Three lists ship with the repo. Every hostname was checked **from a server
abroad** to complete a TLS 1.3 handshake, negotiate HTTP/2, and present a
certificate covering its own name — the three things a Reality target must do.

| File | Contents |
| --- | --- |
| `sni-1000.txt` | 1000 foreign hostnames, 764 organisations |
| `sni-1000-v2.txt` | 1000 more, sharing nothing with the first |
| `sni-1000-ir.txt` | 1000 domestic Iranian hostnames |

The foreign lists are ordered **infrastructure-first**: `api.`, `cdn.`, `edge.`,
`dl.`, `static.` endpoints before front pages. Front-page domains of well known
brands are the first names a shaper learns, which is why they tend to be the
first to lose upload throughput, while the same companies' telemetry and update
endpoints keep working. The first 300 entries contain no `www.` homepage at all,
so `--limit 300` gives you the quiet endpoints only.

The Iranian list is ordered the opposite way — big recognisable sites first —
because a domestic SNI should look like ordinary local traffic, and a well known
homepage does that better than an obscure endpoint.

**The Iranian list is flaky by nature.** Measured back to back, eight foreign
SNIs came back 8/8 on four consecutive runs while eight Iranian SNIs came back
3/8, 7/8, 5/8, 6/8. Nothing about the SNIs changed — reaching Iranian hosts from
outside is simply less reliable. Run a domestic scan a few times and keep what
passes consistently.

### Building your own list

```bash
python3 tools/build_sni_candidates.py > candidates.txt
python3 tools/validate_sni.py candidates.txt --json report.json > verified.txt
python3 tools/rank_sni.py report.json --limit 1000 --pin your.known.good.host
```

Run the validator **on the server that will host the inbounds** — what matters
is whether that machine can reach the target.

---

## Scanning from several machines at once

Comparing SNIs across ISPs means running the client from more than one
connection. That works, but not by simply starting the client twice.

The server keeps **one** Xray config and restarts Xray on every change, so a
second client applying its own config replaces the first client's inbounds and
cuts its transfers mid-flight. Measured with three clients against one server:

```
without --use-existing   client1:  0/40   client2: 38/40   client3: 39/40
with    --use-existing   client1: 39/40   client2: 34/40   client3: 40/40
```

So publish the inbounds once, then have every machine reuse them:

```bash
# once, from any machine
python client-speedScanner.py --server <IP> --api-port 8080 \
    --sni-file sni-1000.txt --batch-size 1000 --skip-speed

# then on every machine, in parallel
python client-speedScanner.py --server <IP> --api-port 8080 \
    --sni-file sni-1000.txt --use-existing --workers 16 --upload-seconds 5
```

`--use-existing` reads the live SNI-to-port map and applies nothing, so no
client can disturb another. Every machine tests the same inbounds on the same
server, which is what makes the runs comparable.

1000 inbounds cost about 550 MB of RAM on the server. Publish 300–500 instead if
memory is tight.

---

## Options

| Flag | Meaning |
| --- | --- |
| `--sni-file FILE` | List to scan, one hostname per line |
| `--limit N` | Only the first N of the file. The lists are pre-ranked, so this takes the best N |
| `--workers N` | Parallel probes (default 8). Upload always stays serial, so this does not shorten the upload pass |
| `--upload-seconds N` | Time budget per upload measurement (default 10) |
| `--upload-mb N` | Sample ceiling per SNI (default 16). Raise it if your uplink is above ~13 Mbps and numbers look noisy |
| `--probe-timeout N` | Seconds to wait for a tunnel to connect (default 5). Raise on a slow link |
| `--use-existing` | Scan the config already live on the server. Required for concurrent clients |
| `--skip-speed` | Reachability and latency only, no data transferred |
| `--with-download` | Also measure download (off by default) |
| `--top N` | Benchmark only the N fastest survivors. Default 0 = all |
| `--phased` | Probe everything first, then upload-test everything. Clean latency and jitter, slower to first result |
| `--probe-gate` | Drop an SNI when its probe fails, instead of upload-testing it anyway |
| `--transport` | tcp, websocket, grpc, http2, xhttp, quic, splithttp |
| `--shuffle` | Randomise the file order (defeats the pre-ranking) |

### Reading the score

```
default            score = 0.75 x upload + 0.25 x latency
--phased           score = 0.65 x upload + 0.25 x latency + 0.10 x jitter
--with-download    upload weight drops to 0.45, download takes 0.20
```

Each term is normalised against the best value in the same run, so scores rank
SNIs *within one scan* and are not comparable across scans.

---

## Troubleshooting

**`curl .../health` is refused** — the service is not running. `systemctl status
sniscanner`, and `tail -40 /var/log/sniscanner.log`.

**`curl .../health` times out** — the port is filtered. Open it in the VPS
firewall *and* in your provider's external firewall or security group. The
inbound range (`30000-31000` by default) needs opening too, not just the API
port.

**Everything fails at stage 1** — usually the inbound port range is not
reachable from your machine. Test one directly: `curl -v telnet://<IP>:30000`.

**The API is on a port you did not ask for** — the server shifts to the next
free port when the requested one is taken. The port it actually bound is printed
at startup and in `/var/log/sniscanner.log`.

**Every SNI looks dead** — PySocks is probably missing. `requests` cannot open a
SOCKS proxy without it, and the failure looks identical to a dead tunnel.

**Upload numbers swing between runs on the same SNI** — your uplink is fast
enough that `--upload-mb 16` ends the sample before `--upload-seconds` does, so
the measurement lands inside TCP slow start. Raise `--upload-mb`.

**An SNI you know works is reported failing** — the probe is an HTTP request to
`speed.cloudflare.com` *through the tunnel*, not a ping to the SNI, so it can
time out on a slow link while the tunnel is fine. It is not a verdict: the SNI
still gets upload-tested and that decides. Raise `--probe-timeout` if it happens
often.

---

## What this fork changed

Upstream tells you which SNIs connect. Everything below came out of making it
tell you which ones are still fast, with the measurement that exposed each bug.

**Upload benchmarking.** The feature that was missing. Each measurement is sized
from a short calibration run to land near a time budget, instead of a fixed
payload that finishes instantly on a fast link and stalls for minutes on a slow
one.

**One inbound per SNI, each with its own target.** Upstream put a whole batch
into one inbound whose Reality target was the batch's *first* SNI. That produces
false negatives — with `target = www.cloudflare.com`, testing `dl.google.com`
fails 4 times out of 4, and works immediately once the target matches — and
false positives, where a domain that does not resolve at all reports as working
because it is in the `serverNames` list you just generated. That bogus SNI then
ranks first, becomes the target for the next stage, and takes the whole run down
with it.

**Parallel scanning that is actually parallel.** Upstream hardcoded the client's
SOCKS inbound to port 1080 for every worker *and* called `kill_all_xray()` at the
top of each worker, so with the default five workers each one killed the other
four and then fought over one port.

**Timeouts that fire.** `requests` treats a scalar `timeout` as both the connect
and the read budget, so a dead tunnel burned the whole value. Worse, the upload
body was a generator, which makes `requests` fall back to chunked encoding — and
on that path urllib3 never applies the timeout to the socket at all. Against a
deliberately stalling proxy, a sized body failed in 5 seconds while the identical
request with a generator body was still hanging after 75. A dead SNI now costs
about five seconds instead of a minute.

**Restarts that survive a big config.** Wait for ports to actually free before
restarting Xray, clear the systemd failed state first (five failed starts leave
the unit refusing to start at all), and skip ports another process holds — one
occupied port in the middle of a range used to abort a config of a thousand
inbounds.

**Kills that hit only our own process.** `pkill -9 xray` is a substring match,
so it also kills the `xray-linux-amd64` that an x-ui panel runs, disconnecting
that panel's customers on every config apply. Both sides now kill only the
processes they started.

**Guard rails on the server.** It refuses to kill a recognised service to claim
a port — upstream would run `lsof -ti:443 | kill -9` to take port 443, which on
a web server means killing nginx or LiteSpeed — and aborts on startup when a
proxy panel is already running.

**Smaller fixes.** `socks5h` so DNS resolves inside the tunnel rather than
through the censored resolver; correct URI transport names (`ws`, `h2`) so the
generated links actually import; a discarded warm-up sample before latency
measurement, without which the server's cold handshake showed as 75 ms of jitter
on a link whose real jitter was under 10; PySocks added to the installer.

---

## Licence

Upstream ships no licence file, so the original code remains under its author's
copyright. This fork is published with their work attributed and linked.
