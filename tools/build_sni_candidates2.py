#!/usr/bin/env python3
"""
Second batch of Reality SNI candidates.

Broadens the first batch outward: European and Asian regional infrastructure,
more CDN and object-storage edges, universities, mirrors, retail, telecom and
industry. Same bias as batch one toward endpoints that carry a lot of traffic
without carrying a famous name.

Output: one hostname per line on stdout.
"""

CANDIDATES = []


def add(*names):
    CANDIDATES.extend(names)


# ---------------------------------------------------------------------------
# Object storage and edge endpoints - high capacity, low profile
# ---------------------------------------------------------------------------
add(
    'storage.bunnycdn.com', 'storage.googleapis.com', 'ams3.digitaloceanspaces.com',
    'fra1.digitaloceanspaces.com', 'nyc3.digitaloceanspaces.com',
    's3.wasabisys.com', 's3.eu-central-2.wasabisys.com', 'wasabi.com',
    'gateway.storjshare.io', 'link.storjshare.io', 'www.backblaze.com',
    'f000.backblazeb2.com', 'api.backblazeb2.com', 's3.us-west-000.backblazeb2.com',
    's3.filebase.com', 'ipfs.io', 'cloudflare-ipfs.com', 'gateway.pinata.cloud',
    'objectstorage.eu-amsterdam-1.oraclecloud.com', 'nbg1.your-objectstorage.com',
    'fsn1.your-objectstorage.com', 'hel1.your-objectstorage.com',
    's3.eu-central-1.ionoscloud.com', 's3.pub1.infomaniak.cloud',
    's3.fr-par.scw.cloud', 's3.nl-ams.scw.cloud', 'rbx.io.cloud.ovh.net',
    'sbg.io.cloud.ovh.net', 'gra.io.cloud.ovh.net',
)

# ---------------------------------------------------------------------------
# More Google / Apple / Microsoft edge names
# ---------------------------------------------------------------------------
add(
    'lh4.googleusercontent.com', 'lh5.googleusercontent.com', 'lh6.googleusercontent.com',
    'books.google.com', 'news.google.com', 'drive.google.com', 'docs.google.com',
    'mail.google.com', 'calendar.google.com', 'photos.google.com',
    'keep.google.com', 'meet.google.com', 'chat.google.com', 'groups.google.com',
    'sites.google.com', 'earth.google.com', 'domains.google', 'store.google.com',
    'about.google', 'blog.google', 'ai.google', 'deepmind.google',
    'gemini.google.com', 'notebooklm.google.com', 'labs.google',
    'firebase.google.com', 'console.firebase.google.com', 'analytics.withgoogle.com',
    'pki.goog', 'ocsp.pki.goog', 'crl.pki.goog', 'gvt2.com', 'gvt3.com',
    'securepubads.g.doubleclick.net', 'tpc.googlesyndication.com',
    'pagead2.googlesyndication.com', 'partner.googleadservices.com',
    'aka-cdn.apple.com', 'captive.apple.com', 'time.apple.com',
    'gs-loc.apple.com', 'pancake.apple.com', 'smoot.apple.com',
    'api-glb-aeuc.smoot.apple.com', 'cdn-dynamic.apple.com',
    'diagnostics.apple.com', 'securemetrics.apple.com', 'stocks-data-service.apple.com',
    'news-events.apple.com', 'newsletters.apple.com', 'discussions.apple.com',
    'jobs.apple.com', 'machinelearning.apple.com', 'security.apple.com',
    'assets.msn.com', 'img-s-msn-com.akamaized.net', 'c.msn.com',
    'ntp.msn.com', 'browser.events.data.microsoft.com',
    'self.events.data.microsoft.com', 'watson.telemetry.microsoft.com',
    'dmd.metaservices.microsoft.com', 'ctldl.windowsupdate.com',
    'emdl.ws.microsoft.com', 'amp.azure.net', 'azurewebsites.net',
    'azurefd.net', 'trafficmanager.net', 'servicebus.windows.net',
    'database.windows.net', 'vault.azure.net', 'search.windows.net',
    'cognitiveservices.azure.com', 'openai.azure.com',
)

# ---------------------------------------------------------------------------
# Europe - regional retail, media, telecom, transport
# ---------------------------------------------------------------------------
add(
    'www.rewe.de', 'www.edeka.de', 'www.lidl.de', 'www.aldi-sued.de',
    'www.dm.de', 'www.rossmann.de', 'www.saturn.de', 'www.conrad.de',
    'www.notebooksbilliger.de', 'www.alternate.de', 'www.cyberport.de',
    'www.thomann.de', 'www.douglas.de', 'www.hm.com', 'www.zara.com',
    'www.ikea.com', 'www.decathlon.de', 'www.adidas.de', 'www.puma.com',
    'www.nike.com', 'www.aboutyou.de', 'www.asos.com', 'www.zalando.com',
    'www.bahn.de', 'www.deutschebahn.com', 'www.flixbus.de', 'www.sbb.ch',
    'www.oebb.at', 'www.sncf.com', 'www.trenitalia.com', 'www.renfe.com',
    'www.klm.com', 'www.airfrance.fr', 'www.britishairways.com',
    'www.swiss.com', 'www.austrian.com', 'www.eurowings.com',
    'www.turkishairlines.com', 'www.emirates.com', 'www.qatarairways.com',
    'www.ing.de', 'www.dkb.de', 'www.commerzbank.de', 'www.deutsche-bank.de',
    'www.sparkasse.de', 'www.n26.com', 'www.revolut.com', 'www.wise.com',
    'www.allianz.de', 'www.axa.de', 'www.generali.de', 'www.munichre.com',
    'www.ard.de', 'www.zdf.de', 'www.tagesschau.de', 'www.wdr.de',
    'www.br.de', 'www.ndr.de', 'www.arte.tv', 'www.rtl.de',
    'www.prosieben.de', 'www.sat1.de', 'www.bild.de', 'www.stern.de',
    'www.focus.de', 'www.handelsblatt.com', 'www.wiwo.de', 'www.n-tv.de',
    'www.t-online.de', 'www.web.de', 'www.gmx.net', 'www.freenet.de',
    'www.chefkoch.de', 'www.wetter.com', 'www.wetteronline.de',
    'www.autoscout24.de', 'www.kleinanzeigen.de', 'www.stepstone.de',
    'www.xing.com', 'www.gutefrage.net', 'www.duden.de', 'www.dict.cc',
    'www.leo.org', 'www.pons.com', 'www.linguee.de', 'www.deepl.com',
    'api.deepl.com', 'www.bundesregierung.de', 'www.bund.de',
    'www.destatis.de', 'www.bundesbank.de', 'www.europa.eu',
    'european-union.europa.eu', 'ec.europa.eu', 'www.ecb.europa.eu',
)

# ---------------------------------------------------------------------------
# Asia-Pacific
# ---------------------------------------------------------------------------
add(
    'www.rakuten.co.jp', 'www.yahoo.co.jp', 'www.nicovideo.jp',
    'www.pixiv.net', 'i.pximg.net', 'www.dmm.com', 'www.mercari.com',
    'www.line.me', 'obs.line-scdn.net', 'www.nintendo.co.jp',
    'www.sony.co.jp', 'www.panasonic.com', 'www.toshiba.com',
    'www.canon.com', 'www.nikon.com', 'www.fujifilm.com', 'www.epson.com',
    'www.brother.com', 'www.honda.com', 'www.toyota.com', 'www.nissan-global.com',
    'www.naver.com', 'www.daum.net', 'www.kakao.com', 'www.coupang.com',
    'www.hyundai.com', 'www.kia.com', 'www.lge.com',
    'www.flipkart.com', 'www.myntra.com', 'www.paytm.com', 'www.zomato.com',
    'www.swiggy.com', 'www.hotstar.com', 'www.jio.com', 'www.airtel.in',
    'www.irctc.co.in', 'www.nseindia.com', 'www.timesofindia.com',
    'www.ndtv.com', 'www.thehindu.com', 'www.grab.com', 'www.shopee.com',
    'www.tokopedia.com', 'www.bukalapak.com', 'www.lazada.com',
    'www.gojek.com', 'www.traveloka.com', 'www.zalora.com',
    'www.seek.com.au', 'www.abc.net.au', 'www.news.com.au', 'www.telstra.com.au',
    'www.optus.com.au', 'www.woolworths.com.au', 'www.coles.com.au',
    'www.trademe.co.nz', 'www.stuff.co.nz',
)

# ---------------------------------------------------------------------------
# Americas
# ---------------------------------------------------------------------------
add(
    'www.walmart.com', 'www.target.com', 'www.bestbuy.com', 'www.costco.com',
    'www.homedepot.com', 'www.lowes.com', 'www.macys.com', 'www.kohls.com',
    'www.wayfair.com', 'www.chewy.com', 'www.etsy.com', 'www.ebay.com',
    'www.newegg.com', 'www.overstock.com', 'www.staples.com',
    'www.verizon.com', 'www.att.com', 'www.t-mobile.com', 'www.comcast.com',
    'www.xfinity.com', 'www.spectrum.com', 'www.cox.com',
    'www.chase.com', 'www.bankofamerica.com', 'www.wellsfargo.com',
    'www.citi.com', 'www.usbank.com', 'www.capitalone.com',
    'www.americanexpress.com', 'www.discover.com', 'www.visa.com',
    'www.mastercard.com', 'www.fidelity.com', 'www.schwab.com',
    'www.vanguard.com', 'www.robinhood.com', 'www.nasdaq.com', 'www.nyse.com',
    'www.espn.com', 'www.nba.com', 'www.nfl.com', 'www.mlb.com', 'www.nhl.com',
    'www.fifa.com', 'www.uefa.com', 'www.olympics.com', 'www.formula1.com',
    'www.washingtonpost.com', 'www.wsj.com', 'www.usatoday.com',
    'www.npr.org', 'www.forbes.com', 'www.businessinsider.com',
    'www.techcrunch.com', 'www.theverge.com', 'www.wired.com',
    'www.arstechnica.com', 'www.engadget.com', 'www.cnet.com', 'www.zdnet.com',
    'www.tomshardware.com', 'www.anandtech.com', 'www.pcmag.com',
    'www.globo.com', 'www.uol.com.br', 'www.mercadolibre.com',
    'www.mercadolivre.com.br', 'www.americanas.com.br', 'www.magazineluiza.com.br',
    'www.itau.com.br', 'www.bradesco.com.br', 'www.nubank.com.br',
    'www.clarin.com', 'www.eluniversal.com.mx', 'www.televisa.com',
)

# ---------------------------------------------------------------------------
# Universities and research
# ---------------------------------------------------------------------------
add(
    'www.cmu.edu', 'www.caltech.edu', 'www.princeton.edu', 'www.yale.edu',
    'www.columbia.edu', 'www.cornell.edu', 'www.upenn.edu', 'www.uchicago.edu',
    'www.umich.edu', 'www.ucla.edu', 'www.ucsd.edu', 'www.washington.edu',
    'www.utexas.edu', 'www.gatech.edu', 'www.illinois.edu', 'www.wisc.edu',
    'www.nyu.edu', 'www.bu.edu', 'www.northwestern.edu', 'www.duke.edu',
    'www.epfl.ch', 'www.uzh.ch', 'www.unibe.ch', 'www.kit.edu',
    'www.rwth-aachen.de', 'www.tu-berlin.de', 'www.tu-darmstadt.de',
    'www.uni-heidelberg.de', 'www.uni-freiburg.de', 'www.uni-koeln.de',
    'www.uni-bonn.de', 'www.uni-hamburg.de', 'www.hu-berlin.de',
    'www.fu-berlin.de', 'www.uni-stuttgart.de', 'www.uni-goettingen.de',
    'www.mpg.de', 'www.fraunhofer.de', 'www.helmholtz.de', 'www.dfg.de',
    'www.imperial.ac.uk', 'www.ucl.ac.uk', 'www.ed.ac.uk', 'www.manchester.ac.uk',
    'www.kcl.ac.uk', 'www.lse.ac.uk', 'www.warwick.ac.uk', 'www.bristol.ac.uk',
    'www.sorbonne-universite.fr', 'www.polytechnique.edu', 'www.ens.psl.eu',
    'www.tudelft.nl', 'www.uva.nl', 'www.leidenuniv.nl', 'www.uu.nl',
    'www.kuleuven.be', 'www.ugent.be', 'www.dtu.dk', 'www.ku.dk',
    'www.kth.se', 'www.uu.se', 'www.lu.se', 'www.ntnu.no', 'www.uio.no',
    'www.helsinki.fi', 'www.aalto.fi', 'www.polimi.it', 'www.unibo.it',
    'www.uniroma1.it', 'www.upm.es', 'www.ucm.es', 'www.upc.edu',
    'www.nus.edu.sg', 'www.ntu.edu.sg', 'www.hku.hk', 'www.cuhk.edu.hk',
    'www.u-tokyo.ac.jp', 'www.kyoto-u.ac.jp', 'www.snu.ac.kr', 'www.kaist.ac.kr',
    'www.unimelb.edu.au', 'www.sydney.edu.au', 'www.anu.edu.au',
    'www.utoronto.ca', 'www.mcgill.ca', 'www.ubc.ca', 'www.uwaterloo.ca',
    'zenodo.org', 'www.osti.gov', 'pubmed.ncbi.nlm.nih.gov', 'www.ncbi.nlm.nih.gov',
    'www.nih.gov', 'www.cdc.gov', 'www.esrf.fr', 'www.desy.de', 'www.gsi.de',
    'www.dlr.de', 'www.jpl.nasa.gov', 'science.nasa.gov', 'eoimages.gsfc.nasa.gov',
)

# ---------------------------------------------------------------------------
# More developer / mirror infrastructure
# ---------------------------------------------------------------------------
add(
    'mirror.init7.net', 'mirror.netcologne.de', 'ftp.fau.de', 'ftp.tu-chemnitz.de',
    'mirror.dogado.de', 'ftp.halifax.rwth-aachen.de', 'mirror.23m.com',
    'mirror.wtnet.de', 'ftp.uni-bayreuth.de', 'mirrors.xtom.de',
    'mirror.cyberbits.eu', 'mirror.mwt.me', 'ftp.lysator.liu.se',
    'mirror.accum.se', 'ftp.acc.umu.se', 'mirrors.dotsrc.org',
    'ftp.nluug.nl', 'mirror.nl.leaseweb.net', 'mirror.de.leaseweb.net',
    'mirror.us.leaseweb.net', 'mirror.serverion.com', 'mirror.hostiserver.com',
    'packages.microsoft.com', 'packages.gitlab.com', 'apt.releases.hashicorp.com',
    'download.opensuse.org', 'rpm.nodesource.com', 'yum.dockerproject.org',
    'archive.apache.org', 'downloads.apache.org', 'dlcdn.apache.org',
    'www.apache.org', 'httpd.apache.org', 'tomcat.apache.org',
    'kafka.apache.org', 'spark.apache.org', 'airflow.apache.org',
    'www.postgresql.org', 'ftp.postgresql.org', 'apt.postgresql.org',
    'www.mysql.com', 'dev.mysql.com', 'repo.mysql.com', 'mariadb.org',
    'downloads.mariadb.org', 'redis.io', 'download.redis.io',
    'www.mongodb.com', 'repo.mongodb.org', 'www.elastic.co',
    'artifacts.elastic.co', 'www.rabbitmq.com', 'grafana.com',
    'dl.grafana.com', 'prometheus.io', 'github.githubassets.com',
    'avatars.githubusercontent.com', 'gist.github.com', 'docs.github.com',
    'copilot.github.com', 'education.github.com', 'pages.github.com',
    'readthedocs.org', 'readthedocs.io', 'sphinx-doc.org', 'jekyllrb.com',
    'gohugo.io', 'astro.build', 'nextjs.org', 'nuxt.com', 'vuejs.org',
    'react.dev', 'angular.dev', 'svelte.dev', 'vitejs.dev', 'webpack.js.org',
    'babeljs.io', 'eslint.org', 'prettier.io', 'jestjs.io', 'playwright.dev',
    'www.selenium.dev', 'www.cypress.io', 'tailwindcss.com', 'getbootstrap.com',
    'sass-lang.com', 'lessjs.org', 'd3js.org', 'threejs.org', 'p5js.org',
    'developer.chrome.com', 'chromestatus.com', 'chromium.googlesource.com',
    'source.chromium.org', 'bugs.chromium.org', 'webkit.org', 'caniuse.com',
)

# ---------------------------------------------------------------------------
# Industry, energy, logistics, pharma
# ---------------------------------------------------------------------------
add(
    'www.abb.com', 'www.schneider-electric.com', 'www.honeywell.com',
    'www.ge.com', 'www.rockwellautomation.com', 'www.emerson.com',
    'www.mitsubishielectric.com', 'www.yokogawa.com', 'www.omron.com',
    'www.festo.com', 'www.sick.com', 'www.pepperl-fuchs.com', 'www.balluff.com',
    'www.thyssenkrupp.com', 'www.basf.com', 'www.bayer.com', 'www.merckgroup.com',
    'www.pfizer.com', 'www.novartis.com', 'www.roche.com', 'www.sanofi.com',
    'www.astrazeneca.com', 'www.gsk.com', 'www.jnj.com', 'www.abbvie.com',
    'www.siemens-healthineers.com', 'www.philips.com', 'www.medtronic.com',
    'www.shell.com', 'www.bp.com', 'www.totalenergies.com', 'www.eni.com',
    'www.equinor.com', 'www.iberdrola.com', 'www.enel.com', 'www.eon.com',
    'www.rwe.com', 'www.vattenfall.de', 'www.engie.com', 'www.orsted.com',
    'www.maersk.com', 'www.hapag-lloyd.com', 'www.kuehne-nagel.com',
    'www.dbschenker.com', 'www.fedex.com', 'www.ups.com', 'www.tnt.com',
    'www.dpd.com', 'www.gls-group.com', 'www.hermesworld.com',
    'www.caterpillar.com', 'www.deere.com', 'www.komatsu.com', 'www.volvo.com',
    'www.scania.com', 'www.man.eu', 'www.daimlertruck.com', 'www.zf.com',
    'www.continental.com', 'www.mahle.com', 'www.schaeffler.com',
    'www.airbus.com', 'www.boeing.com', 'www.safran-group.com',
    'www.rolls-royce.com', 'www.leonardo.com', 'www.thalesgroup.com',
)

# ---------------------------------------------------------------------------
# Misc high-traffic services
# ---------------------------------------------------------------------------
add(
    'www.wetransfer.com', 'wetransfer.com', 'www.mega.nz', 'mega.nz',
    'www.mediafire.com', 'www.4shared.com', 'pixeldrain.com',
    'gofile.io', 'anonfiles.com', 'www.sendspace.com', 'file.io',
    'www.icloud.com', 'proton.me', 'mail.proton.me', 'account.proton.me',
    'protonvpn.com', 'www.tutanota.com', 'tuta.com', 'www.fastmail.com',
    'www.zoho.com', 'mail.zoho.com', 'www.mail.ru', 'www.yandex.com',
    'yandex.com', 'mc.yandex.ru', 'www.vk.com', 'www.ok.ru',
    'archive.org', 'web.archive.org', 'ia801504.us.archive.org',
    'openlibrary.org', 'www.gutenberg.org', 'annas-archive.org',
    'scholar.archive.org', 'www.jstor.org', 'core.ac.uk', 'doaj.org',
    'orcid.org', 'www.crossref.org', 'doi.org', 'dx.doi.org',
    'www.overleaf.com', 'www.mathworks.com', 'www.wolfram.com',
    'www.wolframalpha.com', 'www.desmos.com', 'www.geogebra.org',
    'www.leetcode.com', 'leetcode.com', 'www.hackerrank.com',
    'www.codewars.com', 'codeforces.com', 'atcoder.jp', 'www.topcoder.com',
    'exercism.org', 'www.freecodecamp.org', 'www.codecademy.com',
    'www.pluralsight.com', 'www.linkedin.com', 'www.datacamp.com',
    'www.udacity.com', 'www.skillshare.com', 'www.masterclass.com',
    'www.ted.com', 'www.brilliant.org', 'www.chess.com', 'lichess.org',
    'www.duckduckgo.com', 'duckduckgo.com', 'html.duckduckgo.com',
    'search.brave.com', 'brave.com', 'www.ecosia.org', 'www.startpage.com',
    'www.qwant.com', 'www.mojeek.com', 'search.marcia.dev',
    'www.speedtest.net', 'c.speedtest.net', 'www.fast.com', 'fast.com',
    'librespeed.org', 'www.whatismyip.com', 'ipinfo.io', 'ifconfig.me',
    'api.ipify.org', 'icanhazip.com', 'ipapi.co', 'ip-api.com',
)


def main():
    seen = set()
    for name in CANDIDATES:
        name = name.strip().lower()
        if name and name not in seen and '.' in name:
            seen.add(name)
            print(name)


if __name__ == '__main__':
    main()
