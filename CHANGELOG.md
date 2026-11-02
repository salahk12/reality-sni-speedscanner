# What this fork changed

Upstream tells you which SNIs connect. Everything here came out of making it
tell you which ones are still *fast*, with the measurement that exposed each
bug. Kept out of the README so that stays short.

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
