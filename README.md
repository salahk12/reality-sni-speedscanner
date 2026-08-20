# Reality SNI Speed Scanner

Find Reality SNIs that are not just reachable, but still **fast to upload
through** from a censored network.

> A fork of [AminDaProgrammer/Master_Reality_SNI_Scanner](https://github.com/AminDaProgrammer/Master_Reality_SNI_Scanner).
> All the original scanner's ideas - the server/client split, the API, generating
> a Reality inbound per SNI - come from there, and the upstream README is kept in
> this repo as [README-upstream.md](README-upstream.md). This fork adds the
> throughput benchmark it lacked and fixes several correctness bugs found while
> building it; every one of them is described below with the measurement that
> exposed it.
>
> Upstream ships no licence file, so the original code is under its author's
> default copyright. Ask them before doing anything with this beyond personal
> use.

The server (a VPS abroad, e.g. Germany) builds Reality inbounds from your SNI
list. The client (your own machine, behind the censored network) connects
through each one and measures whether it works and how fast it uploads. What you
get back is a ranked table plus importable `vless://` links.

Probes run in parallel and each one that succeeds is handed straight to a single
uploader thread, so throughput numbers start appearing within seconds instead of
after the whole list has been probed.

## Why the speed stage matters

The SNI only rides in the TLS handshake, so it is tempting to assume every SNI
performs identically. It does not. DPI systems shape traffic per SNI, so two
SNIs on the same server, same port, same protocol can differ by an order of
magnitude in upload throughput. Latency alone will not show you this — you have
to move real bytes.

## What changed versus upstream

### 1. Upload benchmark (the feature that was missing)

Every SNI that answers a probe is then measured against `speed.cloudflare.com`
for upload throughput, and ranked on a 0-100 score together with the latency the
probe already recorded.

**Upload is the measurement that matters.** Per-SNI shaping bites the upload
path first and hardest: an SNI can hold full download speed while its upload
collapses. Download is therefore off by default; add `--with-download` if you
want it, at the cost of roughly doubling the runtime.

Upload tests run **one at a time, always**. Two concurrent transfers compete for
your own last-mile bandwidth and both numbers come out wrong. Probing stays
parallel because it only moves a few bytes per SNI.

Those two facts are reconciled with a queue rather than with two separate
phases: `--workers` probes feed a single uploader thread, so the uplink is never
shared and yet the first result lands almost immediately. Ctrl+C at any point
leaves a useful set of measurements behind.

The consequence worth knowing: probe latency is measured while an upload is in
flight, so it reads higher than an idle ping. Pass `--phased` to probe
everything first and then upload-test everything, which gives clean latency and
jitter at the cost of no throughput number until every probe is done.

Each upload measurement is sized to land near `--upload-seconds` (default 10):
a short calibration upload sets the rate, then the real sample is sized from it,
reusing the same TCP connection. Too small a payload measures nothing but TCP
slow start; too large a one stalls a slow uplink for minutes on a single SNI.

`--upload-mb` (default 16) caps the sample regardless. Below about 13 Mbps of
uplink the time cap is what binds and every sample runs the full ten seconds;
above that the size ceiling binds and samples get shorter, so raise
`--upload-mb` if your uplink is fast and the numbers look noisy.

### The probe never rejects an SNI on its own

The probe is an HTTP request to `speed.cloudflare.com` **through the tunnel**,
not a ping to the SNI. On a slow or lossy link it can time out while the tunnel
is perfectly usable, so treating it as a verdict throws away working SNIs.

A failed probe therefore means only that no latency reading was obtained. The
SNI still goes to the upload test, and that decides. Observed on a real run:

```
[1/8] statics.basalam.com    U   496.73 Mbps      - ms
```

Its probe failed, its upload did not, and it ranked fifth. Under the old
behaviour it would have been dropped without a number.

When a host has no latency reading, the latency share of the score goes to
upload rather than scoring it as though the link were slow. `--probe-gate`
restores the old drop-on-probe-failure behaviour, and `--probe-timeout` (default
5s) buys the probe more time on a bad link - it also relaxes the connect budget
for the upload, which is what you want since both cross the same link.

### Failures fail fast

A tunnel that accepts the connection but never completes the TLS handshake used
to take about 50 seconds per SNI to give up. Two causes, both fixed:

* `requests` treats a scalar `timeout` as both the connect and the read budget,
  so a dead tunnel burned the whole value. Connect and read budgets are now set
  separately, and the connect phase gives up after five seconds.
* The upload body was a generator, which makes `requests` fall back to chunked
  transfer encoding - and on that code path urllib3 never applies the timeout to
  the socket at all. Measured against a deliberately stalling proxy, a bytes
  body failed in 5 seconds while the identical request with a generator body was
  still hanging after 75. Uploads now always send a sized body.

A dead SNI now costs about five seconds instead of a minute.

### 2. One inbound per SNI, each with its own target (accuracy fix)

Upstream put a whole batch (50 SNIs) into a single inbound whose Reality
`target` was the batch's *first* SNI. The server then relays every handshake to
that one target, whatever SNI the client actually asked for. That breaks the
test in both directions:

* **False negatives.** With `target = www.cloudflare.com`, testing
  `dl.google.com` fails 4 times out of 4 — Cloudflare's edge will not serve a
  Google hostname. Point the target at `dl.google.com` and the same SNI works
  immediately. A healthy SNI gets thrown away because of who happened to be
  first in the batch.
* **False positives.** A domain that does not exist at all is reported as
  working, because it *is* in the `serverNames` list you just generated and the
  relay goes to a different, working target. The scan ends up verifying its own
  configuration rather than the SNI. Worse, that bogus SNI then ranks first and
  becomes the target for stage 2, where it fails to resolve and takes every
  other measurement down with it.

This fork gives each SNI its own inbound on its own port with its own matching
target, so a result means what it claims to mean. All inbounds for a chunk live
in one config, so it still costs a single Xray restart per chunk — no slower
than upstream.

### 3. Parallel scanning actually runs in parallel (the big one)

Upstream hardcoded the client's SOCKS inbound to port `1080` for every worker
*and* called `kill_all_xray()` at the top of each worker. With the default of 5
workers, every worker killed the other four and then fought over one port. In
practice one SNI got tested and the rest timed out and were recorded as broken.
Each worker now gets its own SOCKS port and only its own process.

### 4. Smaller fixes

* `socks5h://` instead of `socks5://`, so DNS resolves inside the tunnel rather
  than through the local (censored) resolver.
* Xray startup is detected by polling the SOCKS port instead of a fixed
  `sleep(1.5)` — faster on a quick machine, more reliable on a slow one.
* Processes and temp configs are reaped through a context manager, so an
  exception or Ctrl+C no longer leaks Xray instances.
* Generated links use the correct URI transport names (`ws`, `h2`), so they
  import into clients. Upstream emitted `type=websocket` and `type=http2`.
* A warm-up request is discarded before latency sampling; without it the
  server's cold handshake to the target dominated the jitter figure (75 ms of
  pure artifact on a link whose real jitter was under 10 ms).
* Throughput timing starts at the first received chunk, excluding TTFB and the
  TLS handshake from the Mbps figure.
* `PySocks` added to the dependency installer. Without it `requests` cannot open
  a SOCKS proxy at all, and the failure looks like every SNI being dead.

## Scanning from several machines at once

Comparing SNIs across ISPs means running the client from more than one
connection. That works, but not by simply starting the client twice.

The server keeps **one** Xray config and restarts Xray on every change, so a
second client applying its own config replaces the first client's inbounds and
cuts its transfers mid-flight. Measured with three clients against one server:

```
without --use-existing   client1: 0/40   client2: 38/40   client3: 39/40
with    --use-existing   client1: 39/40  client2: 34/40   client3: 40/40
```

The client that lost is not unlucky, it is the one whose inbounds another client
replaced.

So set the inbounds up once, then have every machine reuse them:

```bash
# once, from any machine: publish the whole list as one config
python3 client-speedScanner.py --server <IP> --api-port 8080 \
    --sni-file sni-1000.txt --batch-size 1000 --skip-speed

# then, on every machine including that one, in parallel
python3 client-speedScanner.py --server <IP> --api-port 8080 \
    --sni-file sni-1000.txt --use-existing --workers 16 --upload-seconds 10
```

`--use-existing` reads the live SNI-to-port map from `/api/portmap` and applies
nothing, so no client can disturb another. Each machine writes its own
`results/` directory, and the runs are directly comparable because every machine
is testing the same inbounds on the same server.

Hosting the whole list at once is the part that makes this possible. 1000
dedicated Reality inbounds cost about 550 MB of RSS and bind 1000 ports, which
a 1 GB VPS will not survive comfortably - use `--limit` to publish 300 or 500
instead if memory is tight.

Two things to get right on the server first:

* **Reserve the port range.** If `net.ipv4.ip_local_port_range` starts below the
  inbound range, an outgoing connection can grab a port in the middle of it and
  Xray aborts on the first bind failure rather than skipping it. Check with
  `sysctl net.ipv4.ip_local_port_range`; if it overlaps, reserve the range:

  ```bash
  sysctl -w net.ipv4.ip_local_reserved_ports="30000-31000"
  echo 'net.ipv4.ip_local_reserved_ports = 30000-31000' >> /etc/sysctl.conf
  ```

  The server also skips any port it finds occupied and logs it, so an unrelated
  listener sitting inside the range no longer breaks the whole config.

* **Bandwidth.** Every client's upload crosses the server's uplink to
  Cloudflare. A handful of home connections will not trouble a gigabit VPS, but
  the server's own link becomes the ceiling once the clients' combined upload
  approaches it.

## Where to run the server component

**Use a clean, disposable VPS.** Not a box that serves anything you care about.

The server component rewrites `/usr/local/etc/xray/config.json` and runs
`pkill -9 xray` on every config change. On a live 3x-ui / x-ui / Marzban host
that kills the panel's own Xray process and drops every connected customer. It
also offers port 443 by default and, upstream, would run `lsof -ti:443 | kill -9`
to take it — which on a web server means killing nginx or LiteSpeed, so the site
and any Telegram webhook go down with it.

This fork now refuses both: it will not kill a recognised service to claim a
port, and it aborts on startup if a panel or a foreign Xray is already running
unless you explicitly confirm. Those are guard rails, not a licence to run it on
a production host.

## Install

On both machines:

```bash
python3 dependencies-autoInstaller.py     # installs requests, PySocks, Xray-core
```

## Run

**Server (the VPS abroad):**

```bash
sudo python3 server-sniScanner.py
```

It prints the Reality port, API port and UUID. **Use the API port it prints** —
it shifts to the next free port when the one you asked for is taken, so it is
not always 8080. Leave it running.

Then confirm from your own machine before starting a scan:

```bash
curl http://<SERVER_IP>:<API_PORT>/health     # expects {"status": "ok", ...}
```

If that times out, the port is filtered: open it in the VPS firewall *and* in
your provider's external firewall or security group. If it is refused, the
server component is not running.

**Client (your machine):**

```bash
python3 client-speedScanner.py \
    --server <SERVER_IP> --api-port 8080 \
    --sni-file sni-1000.txt --limit 300 \
    --transport tcp --workers 8
```

Results land in `results/` as `.html` (sortable report), `.csv`, `.json`,
`.txt`, and `_links.txt` (one `vless://` per line, ready to import).

### Firewall

The dedicated-inbound mode needs a port range open on the server, by default
`30000` upward, one port per SNI in a chunk (so `30000–30079` at the default
`--batch-size 80`). The server tries to open it automatically through `ufw` or
`firewalld`; on a provider with an external firewall you must open it there
yourself. If you cannot open a range at all, `--legacy` falls back to upstream's
single-port behaviour — but read the false-positive/false-negative section above
first, because those verdicts cannot be trusted.

### Traffic and time budget

The upload pass moves real data, serially, over every reachable SNI. Cost per
SNI is whatever your uplink pushes in `--upload-seconds` plus about two seconds
of tunnel setup, so on a 2 Mbps home upload that is roughly 2.5 MB and twelve
seconds each. Two hundred reachable SNIs is then about 40 minutes and 500 MB.

Because probing overlaps the uploads, that figure is very close to the total
runtime: the serial upload pass is the long pole and no amount of `--workers`
shortens it.

The client prints both estimates before it starts, and Ctrl+C saves everything
measured so far. Narrow the run with `--top` if the estimate is too long.

## The bundled SNI list

`sni-1000.txt` holds 1000 hostnames across 764 organisations, each verified from
a German server to complete a TLS 1.3 handshake, negotiate HTTP/2, and present a
certificate covering its own name: the three things a Reality target has to do.
Built and checked with the scripts in `tools/`:

```bash
python3 tools/build_sni_candidates.py  > candidates.txt
python3 tools/build_sni_candidates2.py >> candidates.txt
python3 tools/validate_sni.py candidates.txt --json report.json > verified.txt
python3 tools/rank_sni.py report.json --limit 1000 --pin your.known.good.host
```

Run the validator **from the server that will host the inbounds**, not from your
own machine: what matters is whether that server can reach the target.

The list is ordered infrastructure-first, with api / cdn / edge / dl / static /
storage endpoints ahead of front pages. The first 300 entries contain no `www.`
homepage at all, so `--limit 300` gives you the quiet endpoints only. That
ordering is deliberate: front-page domains of well known brands are the first
names a traffic shaper learns, which is why they tend to be the first to lose
upload throughput, while the same companies' telemetry and update endpoints keep
working. A per-organisation cap of six stops any single provider from dominating
the list, so one company being shaped cannot take the whole list down with it.

Field evidence beats the heuristic: `--pin` forces hostnames you have already
proven to the top regardless of the cap.

### A second, disjoint list

`sni-1000-v2.txt` is another 1000 hostnames sharing **nothing** with the first
list - 2000 distinct SNIs between them. It reaches further afield: the Nordics
and eastern Europe, Turkey and the Gulf, Africa, more of south and south-east
Asia and Latin America, sport, aviation, hospitality, government bodies and a
long tail of open-source projects.

Part of it was generated combinatorially, by trying `api.`, `cdn.`, `static.`,
`assets.`, `img.`, `media.`, `files.` and `edge.` against large apex domains.
Most of those do not resolve and the validator discards them cheaply, but the
ones that survive are exactly the quiet endpoints the ranking wants.

That trick needs a guard. Many SaaS platforms answer every subdomain from one
wildcard record, so `static.`, `files.` and `img.` of the same apex all land on
the same CDN edge with the same certificate - names that look independent but
share a fate. The validator therefore records the IP each name actually
connects to, and `--per-subnet` (default 2) limits how many hostnames in the
list may share a /24. Without it, 94 of the first 100 entries were wildcard
aliases of a handful of endpoints; with it the list spans 911 distinct /24s.

Build a further disjoint list the same way:

```bash
python3 tools/rank_sni.py report.json --exclude sni-1000.txt \
    --exclude sni-1000-v2.txt --limit 1000
```

### The Iranian list

`sni-1000-ir.txt` is 1000 domestic Iranian hostnames, built with
`tools/build_sni_candidates_ir.py` plus a sample of the 114k `.ir` domains that
ship with upstream. 10325 candidates were checked and 4208 passed.

That validation step is not optional here. A domestic SNI is only usable if the
Reality server abroad can still reach it on 443, and a good many Iranian sites
refuse foreign IP space outright - which is invisible until you measure it from
the server that will host the inbounds.

It is ranked differently from the foreign lists. `--no-infra-bias` turns off the
preference for quiet `api.`/`cdn.` endpoints, because the goal of a domestic SNI
is the opposite: to look like ordinary local traffic, and a well known homepage
does that better than an obscure endpoint. `--prefer` puts the curated big sites
ahead of the long tail, so the first 100 entries are all recognisable names -
Aparat, Digikala, Divar, ArvanCloud, IRNA, Zarinpal and so on - and the sampled
`.ir` domains follow.

`--per-subnet` is set to 999 for this list. Many Iranian sites sit behind the
same few domestic CDNs, and sharing an edge is unavoidable rather than a flaw.

**Expect it to be flaky.** Measured back to back from a German server, eight
foreign SNIs came back 8/8 on four consecutive runs, while eight Iranian SNIs
came back 3/8, 7/8, 5/8 and 6/8. Nothing about the SNIs changed between runs -
reaching Iranian hosts from outside is simply less reliable than reaching a CDN
edge in Europe. Run a domestic scan a few times and keep the SNIs that pass
consistently, rather than trusting a single pass.

### A domestic list

`sni-1000-ir.txt` is 1000 Iranian hostnames, disjoint from both lists above.
Built from `tools/build_sni_candidates_ir.py` - banks, news agencies, the big
consumer platforms, universities, government bodies, Iranian CDNs and ISPs -
topped up from the 114k-domain `domains.txt` that ships with upstream.

Three things make this list different to build, and all three are measured
rather than assumed:

* **The server abroad has to reach the target.** Many Iranian sites refuse
  foreign IP space outright, and no amount of guessing substitutes for trying
  it from the machine that will host the inbounds.
* **The domain has to actually be hosted in Iran.** A third of the candidates
  that passed TLS validation turned out to resolve to Canada, Germany or the
  UK - Iranian brands on foreign hosting, which defeats the point of a domestic
  SNI entirely. The validator records the IP each name connects to, those are
  geolocated, and anything not landing in Iran is dropped. `domains.txt` is not
  purely Iranian either: `duckduckgo.com`, `www.cloudflare.com` and
  `upload.wikimedia.org` are all in it.
* **The ordering flips.** `--no-infra-bias` turns off the "prefer quiet API
  endpoints" rule that the foreign lists use. That rule exists because famous
  foreign brands are the first names a shaper learns; a domestic list wants the
  opposite, since the goal is to look like ordinary local traffic and a well
  known homepage does that better than an obscure endpoint. `--prefer` puts the
  curated big sites ahead of the long tail.

`--per-subnet` is set high for this list: Iranian sites cluster heavily on a few
hosting providers, and sharing an IP is expected rather than a defect.

**Use fewer workers here.** Iranian sites behind local CDNs rate-limit repeated
TLS handshakes from one foreign address. Hostnames that fail at `--workers 16`
pass at `--workers 1`, so a failure on this list is weaker evidence than a
failure on the others. Around six workers, sampled runs land at 19-22 out of 25
reachable, and re-running moves individual results - prefer SNIs that survive
more than one scan.

## Useful flags

| Flag | Meaning |
| --- | --- |
| `--top N` | Benchmark only the N fastest survivors. Default 0 = all. Only meaningful with `--phased` |
| `--skip-speed` | Probe only: reachability and latency, no data transfer |
| `--phased` | Probe everything, then upload-test everything. Clean latency and jitter, slower to first result |
| `--upload-seconds` | Seconds cap per upload measurement (default 10) |
| `--probe-timeout` | Seconds to wait for a tunnel to connect (default 5). Raise on a slow link |
| `--probe-gate` | Drop an SNI when its probe fails, instead of upload-testing it anyway |
| `--use-existing` | Scan the config already live on the server, applying nothing. Required for concurrent clients |
| `--upload-mb` | Upload ceiling per SNI; the time cap usually hits first |
| `--with-download` | Also measure download (off by default) |
| `--download-mb` / `--max-download-mb` / `--time-cap` | Download tuning |
| `--ping-samples` | Latency samples per SNI in stage 2 (default 5) |
| `--batch-size` | SNIs per Xray restart (default 80) |
| `--base-port` | First port of the dedicated-inbound range (default 30000) |
| `--limit` / `--shuffle` | Take the first N of the SNI file, optionally shuffled |
| `--legacy` | Upstream shared-target mode. Unreliable — see above |

## Reading the score

```
default              score = 0.75 x upload + 0.25 x latency
--phased             score = 0.65 x upload + 0.25 x latency + 0.10 x jitter
--with-download      upload weight drops to 0.45, download takes 0.20
```

Jitter only carries weight when it was actually measured, which is `--phased`
only; otherwise its share goes to upload.

Each term is normalised against the best value in the run, so the score ranks
SNIs *within one scan* and is not comparable across scans. Upload carries the
most weight because that is where per-SNI shaping shows up first.

## A note on the generated links

The `vless://` links point at the scan inbounds, which disappear when the scan
ends or the next chunk is applied. They are there so you can import one and
confirm the result by hand. Once you have picked a winning SNI, configure it
properly on your real panel.
