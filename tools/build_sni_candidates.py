#!/usr/bin/env python3
"""
Build a candidate SNI list for Reality.

Weighted toward infrastructure, API and edge hostnames rather than famous
homepages. Front-page domains of well known brands are the first thing traffic
shapers learn to recognise, which is why they tend to be the first to lose
upload throughput; the quiet endpoints that the same companies use for app
telemetry, updates and media delivery survive much longer.

Output: one hostname per line on stdout.
"""

CANDIDATES = []


def add(*names):
    CANDIDATES.extend(names)


# ---------------------------------------------------------------------------
# Apple - lots of quiet, high-capacity edge endpoints
# ---------------------------------------------------------------------------
add(
    'amp-api-edge.apps.apple.com', 'amp-api.apps.apple.com', 'apps.apple.com',
    'itunes.apple.com', 'api.apple-cloudkit.com', 'gateway.icloud.com',
    'p01-content.icloud.com', 'p23-content.icloud.com', 'setup.icloud.com',
    'cdn.apple-cloudkit.com', 'gsp64-ssl.ls.apple.com', 'gsp-ssl.ls.apple.com',
    'configuration.apple.com', 'gdmf.apple.com', 'mesu.apple.com',
    'swcdn.apple.com', 'swscan.apple.com', 'updates.cdn-apple.com',
    'osxapps.itunes.apple.com', 'appldnld.apple.com', 'iosapps.itunes.apple.com',
    'is1-ssl.mzstatic.com', 'is2-ssl.mzstatic.com', 'is3-ssl.mzstatic.com',
    'is4-ssl.mzstatic.com', 'is5-ssl.mzstatic.com', 'a1.mzstatic.com',
    'a2.mzstatic.com', 'a3.mzstatic.com', 'a4.mzstatic.com', 'a5.mzstatic.com',
    'play.itunes.apple.com', 'init.itunes.apple.com', 'su.itunes.apple.com',
    'xp.apple.com', 'metrics.apple.com', 'weather-data.apple.com',
    'gspe1-ssl.ls.apple.com', 'gspe35-ssl.ls.apple.com', 'cl1.apple.com',
    'cl2.apple.com', 'cl3.apple.com', 'cl4.apple.com', 'cl5.apple.com',
    'bag.itunes.apple.com', 'books.itunes.apple.com', 'tv.apple.com',
    'sylvan.apple.com', 'devimages-cdn.apple.com', 'developer.apple.com',
    'support.apple.com', 'www.apple.com', 'store.apple.com', 'music.apple.com',
    'podcasts.apple.com', 'icloud.com', 'www.icloud.com', 'business.apple.com',
    'school.apple.com', 'mdmenrollment.apple.com', 'deviceenrollment.apple.com',
    'humb.apple.com', 'ppq.apple.com', 'crl.apple.com', 'ocsp.apple.com',
    'valid.apple.com', 'certs.apple.com', 'idmsa.apple.com', 'appleid.apple.com',
)

# ---------------------------------------------------------------------------
# Google / YouTube infrastructure
# ---------------------------------------------------------------------------
add(
    'dl.google.com', 'redirector.gvt1.com', 'r1---sn-4g5e6nez.gvt1.com',
    'storage.googleapis.com', 'firebasestorage.googleapis.com',
    'fcm.googleapis.com', 'firebaseinstallations.googleapis.com',
    'firebaseremoteconfig.googleapis.com', 'crashlyticsreports-pa.googleapis.com',
    'play.googleapis.com', 'android.googleapis.com', 'safebrowsing.googleapis.com',
    'people-pa.googleapis.com', 'youtubei.googleapis.com',
    'translate.googleapis.com', 'maps.googleapis.com', 'fonts.googleapis.com',
    'fonts.gstatic.com', 'www.gstatic.com', 'ssl.gstatic.com',
    'encrypted-tbn0.gstatic.com', 'lh3.googleusercontent.com',
    'yt3.ggpht.com', 'i.ytimg.com', 's.ytimg.com', 'www.youtube.com',
    'accounts.google.com', 'apis.google.com', 'clients1.google.com',
    'clients2.google.com', 'clients3.google.com', 'clients4.google.com',
    'clients6.google.com', 'update.googleapis.com', 'tools.google.com',
    'chromewebstore.googleapis.com', 'edgedl.me.gvt1.com',
    'commondatastorage.googleapis.com', 'bigquery.googleapis.com',
    'compute.googleapis.com', 'container.googleapis.com', 'run.googleapis.com',
    'cloudfunctions.googleapis.com', 'pubsub.googleapis.com',
    'aiplatform.googleapis.com', 'generativelanguage.googleapis.com',
    'oauth2.googleapis.com', 'www.googleapis.com', 'ampcid.google.com',
    'googleads.g.doubleclick.net', 'stats.g.doubleclick.net',
    'developers.google.com', 'cloud.google.com', 'source.cloud.google.com',
)

# ---------------------------------------------------------------------------
# Microsoft / Azure / Xbox
# ---------------------------------------------------------------------------
add(
    'download.microsoft.com', 'download.windowsupdate.com',
    'tlu.dl.delivery.mp.microsoft.com', 'geo.prod.do.dsp.mp.microsoft.com',
    'displaycatalog.mp.microsoft.com', 'licensing.mp.microsoft.com',
    'purchase.mp.microsoft.com', 'settings-win.data.microsoft.com',
    'login.microsoftonline.com', 'graph.microsoft.com', 'outlook.office365.com',
    'outlook.office.com', 'substrate.office.com', 'config.office.com',
    'officecdn.microsoft.com', 'ocsp.msocsp.com', 'www.microsoft.com',
    'go.microsoft.com', 'aka.ms', 'management.azure.com', 'portal.azure.com',
    'blob.core.windows.net', 'azureedge.net', 'msedge.net',
    'azure.microsoft.com', 'learn.microsoft.com', 'docs.microsoft.com',
    'visualstudio.microsoft.com', 'marketplace.visualstudio.com',
    'update.code.visualstudio.com', 'vscode.dev', 'nuget.org',
    'api.nuget.org', 'dev.azure.com', 'dc.services.visualstudio.com',
    'xbox.com', 'www.xbox.com', 'xboxlive.com', 'title.mgt.xboxlive.com',
    'device.auth.xboxlive.com', 'skype.com', 'www.skype.com',
    'teams.microsoft.com', 'bing.com', 'www.bing.com', 'edge.microsoft.com',
    'copilot.microsoft.com', 'msn.com', 'www.msn.com', 'live.com',
    'onedrive.live.com', 'storage.live.com', 'linkedin.com', 'www.linkedin.com',
    'static.licdn.com', 'media.licdn.com',
)

# ---------------------------------------------------------------------------
# Amazon / AWS
# ---------------------------------------------------------------------------
add(
    'aws.amazon.com', 'console.aws.amazon.com', 's3.amazonaws.com',
    's3.eu-central-1.amazonaws.com', 's3.eu-west-1.amazonaws.com',
    's3.us-east-1.amazonaws.com', 'ec2.eu-central-1.amazonaws.com',
    'dynamodb.eu-central-1.amazonaws.com', 'sqs.eu-central-1.amazonaws.com',
    'lambda.eu-central-1.amazonaws.com', 'api.ecr.eu-central-1.amazonaws.com',
    'sts.amazonaws.com', 'iam.amazonaws.com', 'cloudfront.net',
    'd1.awsstatic.com', 'a0.awsstatic.com', 'docs.aws.amazon.com',
    'amazon.com', 'www.amazon.com', 'www.amazon.de', 'www.amazon.co.uk',
    'images-na.ssl-images-amazon.com', 'm.media-amazon.com',
    'completion.amazon.com', 'fls-na.amazon.com', 'api.amazon.com',
    'amazonvideo.com', 'atv-ps.amazon.com', 'aiv-cdn.net',
    'twitch.tv', 'www.twitch.tv', 'static.twitchcdn.net', 'gql.twitch.tv',
    'usher.ttvnw.net', 'video-weaver.fra02.hls.ttvnw.net',
    'audible.com', 'www.audible.com', 'goodreads.com', 'www.goodreads.com',
)

# ---------------------------------------------------------------------------
# CDNs - usually excellent Reality targets
# ---------------------------------------------------------------------------
add(
    'cdn.jsdelivr.net', 'fastly.jsdelivr.net', 'gcore.jsdelivr.net',
    'unpkg.com', 'cdnjs.cloudflare.com', 'ajax.googleapis.com',
    'code.jquery.com', 'stackpath.bootstrapcdn.com', 'maxcdn.bootstrapcdn.com',
    'use.fontawesome.com', 'kit.fontawesome.com', 'polyfill.io',
    'cdn.polyfill.io', 'esm.sh', 'cdn.skypack.dev', 'jspm.dev',
    'www.fastly.com', 'api.fastly.com', 'global.prod.fastly.net',
    'www.akamai.com', 'akamaized.net', 'akamaihd.net', 'edgekey.net',
    'edgesuite.net', 'akstat.io', 'go.akamai.com',
    'www.cloudflare.com', 'cloudflare.com', 'developers.cloudflare.com',
    'dash.cloudflare.com', 'speed.cloudflare.com', 'one.one.one.one',
    'workers.dev', 'pages.dev', 'cdn.bunny.net', 'bunnycdn.com',
    'b-cdn.net', 'www.keycdn.com', 'kxcdn.com', 'stackpath.com',
    'gcore.com', 'cdn.gcore.com', 'imgix.net', 'cloudinary.com',
    'res.cloudinary.com', 'cdn.sanity.io', 'cdn.contentful.com',
    'images.ctfassets.net', 'assets.ctfassets.net', 'cdn.shopify.com',
    'cdn.jsdelivr.com', 'cdn77.com', 'www.cdn77.com',
)

# ---------------------------------------------------------------------------
# Device vendors - update / telemetry endpoints
# ---------------------------------------------------------------------------
add(
    'www.samsung.com', 'account.samsung.com', 'api.samsungcloud.com',
    'fota-cloud-dn.ospserver.net', 'fota-secure-dn.ospserver.net',
    'cdn.samsungcloudsolution.com', 'api.samsungosp.com',
    'samsungapps.com', 'apps.samsung.com', 'img.samsungapps.com',
    'www.lg.com', 'lgeapi.com', 'us.lgeapi.com', 'eu.lgeapi.com',
    'www.sony.com', 'www.playstation.com', 'store.playstation.com',
    'gs2-sec.ww.prod.dl.playstation.net', 'zeus.dl.playstation.net',
    'www.mi.com', 'global.miui.com', 'api.io.mi.com', 'cdn.cnbj1.fds.api.mi-img.com',
    'sgp-api.buy.mi.com', 'www.huawei.com', 'consumer.huawei.com',
    'query.hicloud.com', 'logservice.hicloud.com', 'www.oneplus.com',
    'www.oppo.com', 'www.vivo.com', 'www.realme.com', 'www.motorola.com',
    'www.nokia.com', 'www.asus.com', 'dlcdnets.asus.com', 'www.acer.com',
    'www.lenovo.com', 'download.lenovo.com', 'www.dell.com', 'dl.dell.com',
    'www.hp.com', 'ftp.hp.com', 'support.hp.com', 'www.intel.com',
    'downloadmirror.intel.com', 'www.amd.com', 'drivers.amd.com',
    'www.nvidia.com', 'us.download.nvidia.com', 'developer.nvidia.com',
    'www.qualcomm.com', 'www.arm.com', 'www.broadcom.com',
)

# ---------------------------------------------------------------------------
# Gaming
# ---------------------------------------------------------------------------
add(
    'store.steampowered.com', 'steamcommunity.com', 'api.steampowered.com',
    'steamcdn-a.akamaihd.net', 'cdn.cloudflare.steamstatic.com',
    'shared.cdn.steamstatic.com', 'clientconfig.akamai.steamstatic.com',
    'www.epicgames.com', 'store.epicgames.com', 'launcher-public-service-prod06.ol.epicgames.com',
    'fastly-download.epicgames.com', 'epicgames-download1.akamaized.net',
    'www.riotgames.com', 'lol.secure.dyn.riotcdn.net', 'valorant.secure.dyn.riotcdn.net',
    'ddragon.leagueoflegends.com', 'www.ea.com', 'api1.origin.com',
    'www.ubisoft.com', 'public-ubiservices.ubi.com', 'static3.cdn.ubi.com',
    'www.blizzard.com', 'us.battle.net', 'eu.battle.net', 'level3.blizzard.com',
    'blzddist1-a.akamaihd.net', 'www.roblox.com', 'setup.rbxcdn.com',
    'www.nintendo.com', 'ccs.cdn.wup.shop.nintendo.net', 'atum.hac.lp1.d4c.nintendo.net',
    'www.minecraft.net', 'launchermeta.mojang.com', 'resources.download.minecraft.net',
    'libraries.minecraft.net', 'www.gog.com', 'gog-cdn-lumen.secure2.footprint.net',
    'www.itch.io', 'unity.com', 'unitytech.com', 'config.uca.cloud.unity3d.com',
    'www.unrealengine.com', 'cdn1.epicgames.com', 'www.humblebundle.com',
)

# ---------------------------------------------------------------------------
# Media / streaming
# ---------------------------------------------------------------------------
add(
    'www.spotify.com', 'open.spotify.com', 'api.spotify.com',
    'apresolve.spotify.com', 'spclient.wg.spotify.com', 'i.scdn.co',
    'audio-fa.scdn.co', 'www.soundcloud.com', 'api-v2.soundcloud.com',
    'i1.sndcdn.com', 'vimeo.com', 'player.vimeo.com', 'i.vimeocdn.com',
    'f.vimeocdn.com', 'www.netflix.com', 'ipv4-c001-fra001-ix.1.oca.nflxvideo.net',
    'assets.nflxext.com', 'www.disneyplus.com', 'cdn.registerdisney.go.com',
    'www.hulu.com', 'www.hbomax.com', 'www.paramountplus.com',
    'www.deezer.com', 'api.deezer.com', 'e-cdns-files.dzcdn.net',
    'www.tidal.com', 'api.tidal.com', 'www.pandora.com',
    'www.last.fm', 'www.mixcloud.com', 'www.bandcamp.com',
    'www.dailymotion.com', 'static1.dmcdn.net', 'www.tiktok.com',
    'www16-normal-c-useast2a.tiktokv.com', 'p16-sign-va.tiktokcdn.com',
    'lf16-effectcdn.tiktokcdn-us.com', 'mssdk-va.tiktokv.com',
)

# ---------------------------------------------------------------------------
# Developer / package infrastructure
# ---------------------------------------------------------------------------
add(
    'github.com', 'api.github.com', 'raw.githubusercontent.com',
    'objects.githubusercontent.com', 'codeload.github.com',
    'github-releases.githubusercontent.com', 'ghcr.io', 'pkg.github.com',
    'gitlab.com', 'about.gitlab.com', 'registry.gitlab.com',
    'bitbucket.org', 'api.bitbucket.org', 'www.atlassian.com',
    'registry.npmjs.org', 'www.npmjs.com', 'registry.yarnpkg.com',
    'pypi.org', 'files.pythonhosted.org', 'www.python.org', 'python.org',
    'docs.python.org', 'repo.maven.apache.org', 'repo1.maven.org',
    'search.maven.org', 'plugins.gradle.org', 'services.gradle.org',
    'proxy.golang.org', 'sum.golang.org', 'go.dev', 'golang.org',
    'crates.io', 'static.crates.io', 'index.crates.io', 'doc.rust-lang.org',
    'static.rust-lang.org', 'www.rust-lang.org', 'rubygems.org',
    'packagist.org', 'repo.packagist.org', 'getcomposer.org',
    'hub.docker.com', 'registry-1.docker.io', 'auth.docker.io',
    'production.cloudflare.docker.com', 'download.docker.com',
    'quay.io', 'k8s.gcr.io', 'registry.k8s.io', 'kubernetes.io',
    'helm.sh', 'get.helm.sh', 'releases.hashicorp.com', 'www.terraform.io',
    'www.jetbrains.com', 'download.jetbrains.com', 'plugins.jetbrains.com',
    'www.eclipse.org', 'download.eclipse.org', 'nodejs.org', 'deb.nodesource.com',
    'stackoverflow.com', 'api.stackexchange.com', 'cdn.sstatic.net',
    'developer.mozilla.org', 'www.mozilla.org', 'download.mozilla.org',
    'archive.mozilla.org', 'addons.mozilla.org', 'firefox.settings.services.mozilla.com',
)

# ---------------------------------------------------------------------------
# OS and software mirrors - big, fast, and boring to a traffic shaper
# ---------------------------------------------------------------------------
add(
    'archive.ubuntu.com', 'security.ubuntu.com', 'releases.ubuntu.com',
    'cdimage.ubuntu.com', 'changelogs.ubuntu.com', 'de.archive.ubuntu.com',
    'deb.debian.org', 'security.debian.org', 'cdimage.debian.org',
    'ftp.de.debian.org', 'ftp.debian.org', 'download.fedoraproject.org',
    'dl.fedoraproject.org', 'mirrors.fedoraproject.org', 'getfedora.org',
    'geo.mirror.pkgbuild.com', 'archlinux.org', 'mirror.rackspace.com',
    'download.opensuse.org', 'mirrorcache.opensuse.org',
    'mirror.centos.org', 'vault.centos.org', 'yum.oracle.com',
    'dl.rockylinux.org', 'download.rockylinux.org', 'mirrors.almalinux.org',
    'repo.almalinux.org', 'mirror.hetzner.com', 'mirror.leaseweb.com',
    'ftp.gnu.org', 'mirrors.kernel.org', 'cdn.kernel.org', 'www.kernel.org',
    'git.kernel.org', 'ftp.gnome.org', 'download.kde.org',
    'sourceforge.net', 'downloads.sourceforge.net', 'www.videolan.org',
    'get.videolan.org', 'download.virtualbox.org', 'www.virtualbox.org',
    'dl.winehq.org', 'www.libreoffice.org', 'download.documentfoundation.org',
    'ftp.mozilla.org', 'apt.llvm.org', 'releases.llvm.org',
)

# ---------------------------------------------------------------------------
# Cloud / hosting providers
# ---------------------------------------------------------------------------
add(
    'www.digitalocean.com', 'cloud.digitalocean.com', 'api.digitalocean.com',
    'www.linode.com', 'api.linode.com', 'www.vultr.com', 'api.vultr.com',
    'www.hetzner.com', 'console.hetzner.cloud', 'api.hetzner.cloud',
    'www.ovh.com', 'www.ovhcloud.com', 'api.ovh.com', 'www.scaleway.com',
    'api.scaleway.com', 'www.oracle.com', 'cloud.oracle.com',
    'objectstorage.eu-frankfurt-1.oraclecloud.com', 'www.ibm.com',
    'cloud.ibm.com', 'www.alibabacloud.com', 'www.aliyun.com',
    'www.tencentcloud.com', 'www.heroku.com', 'api.heroku.com',
    'www.netlify.com', 'api.netlify.com', 'vercel.com', 'api.vercel.com',
    'www.cloudflare.com', 'www.fly.io', 'api.fly.io', 'railway.app',
    'render.com', 'www.namecheap.com', 'www.godaddy.com', 'www.hostinger.com',
    'www.contabo.com', 'www.ionos.com', 'www.strato.de', 'www.1und1.de',
    'www.plesk.com', 'cpanel.net', 'www.cloudlinux.com',
)

# ---------------------------------------------------------------------------
# SaaS / productivity
# ---------------------------------------------------------------------------
add(
    'www.dropbox.com', 'api.dropboxapi.com', 'content.dropboxapi.com',
    'www.box.com', 'api.box.com', 'www.zoom.us', 'zoom.us', 'api.zoom.us',
    'slack.com', 'api.slack.com', 'edgeapi.slack.com', 'files.slack.com',
    'www.notion.so', 'api.notion.com', 'www.figma.com', 'api.figma.com',
    'www.canva.com', 'www.adobe.com', 'creativecloud.adobe.com',
    'ccmdls.adobe.com', 'prod-rel-ffc-ccm.oobesaas.adobe.com',
    'www.autodesk.com', 'www.salesforce.com', 'login.salesforce.com',
    'www.hubspot.com', 'api.hubapi.com', 'www.zendesk.com',
    'www.intercom.com', 'api-iam.intercom.io', 'www.asana.com',
    'app.asana.com', 'trello.com', 'api.trello.com', 'www.monday.com',
    'www.airtable.com', 'api.airtable.com', 'www.evernote.com',
    'www.grammarly.com', 'www.mailchimp.com', 'www.sendgrid.com',
    'api.sendgrid.com', 'api.twilio.com', 'www.twilio.com',
    'api.stripe.com', 'js.stripe.com', 'www.stripe.com', 'checkout.stripe.com',
    'www.paypal.com', 'api.paypal.com', 'www.klarna.com',
)

# ---------------------------------------------------------------------------
# News, reference, education
# ---------------------------------------------------------------------------
add(
    'www.wikipedia.org', 'en.wikipedia.org', 'de.wikipedia.org',
    'upload.wikimedia.org', 'commons.wikimedia.org', 'www.wikidata.org',
    'www.bbc.com', 'www.bbc.co.uk', 'static.files.bbci.co.uk',
    'www.reuters.com', 'www.bloomberg.com', 'www.cnn.com', 'www.nytimes.com',
    'www.theguardian.com', 'www.economist.com', 'www.ft.com',
    'www.spiegel.de', 'www.zeit.de', 'www.faz.net', 'www.welt.de',
    'www.sueddeutsche.de', 'www.heise.de', 'www.golem.de', 'www.chip.de',
    'www.lemonde.fr', 'www.elpais.com', 'www.corriere.it',
    'www.nature.com', 'www.science.org', 'www.sciencedirect.com',
    'arxiv.org', 'www.jstor.org', 'scholar.google.com', 'www.researchgate.net',
    'www.mit.edu', 'ocw.mit.edu', 'www.stanford.edu', 'www.harvard.edu',
    'www.berkeley.edu', 'www.ethz.ch', 'www.tum.de', 'www.uni-muenchen.de',
    'www.ox.ac.uk', 'www.cam.ac.uk', 'home.cern', 'www.esa.int',
    'www.nasa.gov', 'www.noaa.gov', 'www.who.int', 'www.un.org',
    'www.coursera.org', 'www.edx.org', 'www.udemy.com', 'www.khanacademy.org',
    'www.duolingo.com', 'd35aaqx5ub95lt.cloudfront.net',
)

# ---------------------------------------------------------------------------
# European / regional infrastructure - close to a German server
# ---------------------------------------------------------------------------
add(
    'www.telekom.de', 'www.vodafone.de', 'www.o2online.de', 'www.1und1.net',
    'www.orange.fr', 'www.free.fr', 'www.sfr.fr', 'www.bouyguestelecom.fr',
    'www.vodafone.co.uk', 'www.ee.co.uk', 'www.bt.com', 'www.three.co.uk',
    'www.swisscom.ch', 'www.a1.net', 'www.kpn.com', 'www.telia.se',
    'www.telenor.no', 'www.tim.it', 'www.vodafone.it', 'www.movistar.es',
    'www.de-cix.net', 'www.ams-ix.net', 'www.linx.net', 'www.ripe.net',
    'www.iana.org', 'www.icann.org', 'www.ietf.org', 'datatracker.ietf.org',
    'www.rfc-editor.org', 'www.w3.org', 'www.iso.org', 'www.ieee.org',
    'www.sap.com', 'www.siemens.com', 'www.bosch.com', 'www.bmw.de',
    'www.mercedes-benz.com', 'www.volkswagen.de', 'www.audi.de',
    'www.porsche.com', 'www.lufthansa.com', 'www.dhl.de', 'www.dhl.com',
    'www.zalando.de', 'www.otto.de', 'www.mediamarkt.de', 'www.idealo.de',
    'www.check24.de', 'www.immobilienscout24.de', 'www.mobile.de',
    'www.booking.com', 'www.airbnb.com', 'www.expedia.com',
    'www.tripadvisor.com', 'www.skyscanner.net', 'www.ryanair.com',
)

# ---------------------------------------------------------------------------
# Security / DNS / certificate infrastructure
# ---------------------------------------------------------------------------
add(
    'dns.google', 'cloudflare-dns.com', 'mozilla.cloudflare-dns.com',
    'dns.quad9.net', 'doh.opendns.com', 'dns.adguard.com',
    'dns.nextdns.io', 'doh.cleanbrowsing.org', 'dns.sb', 'doh.dns.sb',
    'letsencrypt.org', 'acme-v02.api.letsencrypt.org', 'r3.o.lencr.org',
    'x1.c.lencr.org', 'crl.identrust.com', 'ocsp.digicert.com',
    'crl3.digicert.com', 'www.digicert.com', 'www.globalsign.com',
    'ocsp.globalsign.com', 'www.sectigo.com', 'crt.sh',
    'www.ssllabs.com', 'www.qualys.com', 'www.virustotal.com',
    'www.shodan.io', 'www.censys.io', 'haveibeenpwned.com',
    'www.eff.org', 'www.torproject.org', 'www.privacyguides.org',
    'www.kaspersky.com', 'www.bitdefender.com', 'www.eset.com',
    'www.malwarebytes.com', 'www.avast.com', 'www.norton.com',
    'www.mcafee.com', 'www.trendmicro.com', 'www.sophos.com',
    'www.fortinet.com', 'www.paloaltonetworks.com', 'www.crowdstrike.com',
    'www.okta.com', 'www.auth0.com', 'www.1password.com', 'www.lastpass.com',
    'www.bitwarden.com', 'vault.bitwarden.com',
)

# ---------------------------------------------------------------------------
# Analytics / telemetry / ad infrastructure - very high volume, very boring
# ---------------------------------------------------------------------------
add(
    'www.google-analytics.com', 'analytics.google.com', 'region1.google-analytics.com',
    'www.googletagmanager.com', 'tagmanager.google.com',
    'connect.facebook.net', 'graph.facebook.com', 'www.facebook.com',
    'static.xx.fbcdn.net', 'scontent.xx.fbcdn.net', 'edge-chat.facebook.com',
    'www.instagram.com', 'i.instagram.com', 'graph.instagram.com',
    'web.whatsapp.com', 'g.whatsapp.net', 'mmg.whatsapp.net',
    'api.mixpanel.com', 'api.amplitude.com', 'api2.amplitude.com',
    'api.segment.io', 'cdn.segment.com', 'browser.sentry-cdn.com',
    'o0.ingest.sentry.io', 'sentry.io', 'www.datadoghq.com',
    'browser-intake-datadoghq.com', 'api.datadoghq.com',
    'cdn.optimizely.com', 'cdn.heapanalytics.com', 'static.hotjar.com',
    'script.hotjar.com', 'cdn.matomo.cloud', 'plausible.io',
    'cdn.usefathom.com', 'static.cloudflareinsights.com',
    'bat.bing.com', 'analytics.twitter.com', 'static.ads-twitter.com',
    'x.com', 'api.x.com', 'abs.twimg.com', 'pbs.twimg.com', 'video.twimg.com',
)

# ---------------------------------------------------------------------------
# Messaging / social / misc large services
# ---------------------------------------------------------------------------
add(
    'telegram.org', 'core.telegram.org', 'web.telegram.org', 'desktop.telegram.org',
    'discord.com', 'discordapp.com', 'cdn.discordapp.com', 'gateway.discord.gg',
    'media.discordapp.net', 'www.reddit.com', 'oauth.reddit.com',
    'i.redd.it', 'preview.redd.it', 'styles.redditmedia.com',
    'www.pinterest.com', 'i.pinimg.com', 'www.quora.com',
    'www.medium.com', 'medium.com', 'cdn-images-1.medium.com',
    'www.tumblr.com', 'www.flickr.com', 'live.staticflickr.com',
    'www.behance.net', 'www.dribbble.com', 'cdn.dribbble.com',
    'unsplash.com', 'images.unsplash.com', 'www.pexels.com',
    'images.pexels.com', 'www.shutterstock.com', 'www.gettyimages.com',
    'signal.org', 'chat.signal.org', 'cdn.signal.org', 'updates2.signal.org',
    'threema.ch', 'www.viber.com', 'www.line-apps.com', 'www.kakaocorp.com',
    'www.wechat.com', 'www.snapchat.com', 'app.snapchat.com',
    'www.twitch.tv', 'www.patreon.com', 'www.kickstarter.com',
    'www.indiegogo.com', 'www.upwork.com', 'www.fiverr.com',
    'www.freelancer.com', 'www.glassdoor.com', 'www.indeed.com',
    'www.coinbase.com', 'api.coinbase.com', 'www.binance.com',
    'api.binance.com', 'www.kraken.com', 'api.kraken.com',
    'www.tradingview.com', 's3.tradingview.com',
)

# ---------------------------------------------------------------------------
# AI / ML services
# ---------------------------------------------------------------------------
add(
    'www.anthropic.com', 'api.anthropic.com', 'claude.ai',
    'openai.com', 'www.openai.com', 'api.openai.com', 'cdn.openai.com',
    'huggingface.co', 'cdn-lfs.huggingface.co', 'cas-bridge.xethub.hf.co',
    'www.kaggle.com', 'storage.googleapis.com', 'pytorch.org',
    'download.pytorch.org', 'www.tensorflow.org', 'storage.tensorflow.org',
    'www.nvidia.com', 'catalog.ngc.nvidia.com', 'www.perplexity.ai',
    'www.midjourney.com', 'replicate.com', 'api.replicate.com',
    'www.runpod.io', 'colab.research.google.com', 'jupyter.org',
    'www.wandb.ai', 'api.wandb.ai', 'mlflow.org',
)


def main():
    seen = set()
    ordered = []
    for name in CANDIDATES:
        name = name.strip().lower()
        if not name or name in seen or '.' not in name:
            continue
        seen.add(name)
        ordered.append(name)
    for name in ordered:
        print(name)


if __name__ == '__main__':
    main()
