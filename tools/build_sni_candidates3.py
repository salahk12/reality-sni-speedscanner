#!/usr/bin/env python3
"""
Third batch of Reality SNI candidates: new organisations, new regions.

Batches one and two covered the big western platforms, CDNs, package
infrastructure and European retail. This batch deliberately goes elsewhere -
Nordic and eastern Europe, Turkey and the Gulf, Africa, more of south-east Asia
and Latin America, sport, aviation, hospitality, government and intergovernmental
bodies, and a long tail of open-source projects.

It also generates infrastructure-style subdomains combinatorially over apex
domains that are known to be large. Most will not resolve; the validator throws
those away cheaply, and the ones that survive are exactly the quiet endpoints
the ranking prefers.

Output: one hostname per line on stdout.
"""

CANDIDATES = []


def add(*names):
    CANDIDATES.extend(names)


# ---------------------------------------------------------------------------
# Nordics and Baltics
# ---------------------------------------------------------------------------
add(
    'www.dnb.no', 'www.nordea.com', 'www.seb.se', 'www.swedbank.se',
    'www.handelsbanken.se', 'www.danskebank.dk', 'www.op.fi', 'www.nordnet.se',
    'www.klarna.se', 'www.izettle.com', 'www.trustly.com', 'www.zettle.com',
    'www.ica.se', 'www.coop.se', 'www.elgiganten.se', 'www.komplett.no',
    'www.power.no', 'www.xxl.no', 'www.jula.se', 'www.clasohlson.com',
    'www.svt.se', 'www.sr.se', 'www.dn.se', 'www.aftonbladet.se',
    'www.expressen.se', 'www.nrk.no', 'www.vg.no', 'www.dr.dk',
    'www.yle.fi', 'www.hs.fi', 'www.ruv.is', 'www.mbl.is',
    'www.telia.fi', 'www.elisa.fi', 'www.dna.fi', 'www.telenor.se',
    'www.tele2.se', 'www.ice.no', 'www.tdc.dk', 'www.telia.dk',
    'www.sj.se', 'www.vy.no', 'www.dsb.dk', 'www.vr.fi', 'www.finnair.com',
    'www.sas.se', 'www.norwegian.com', 'www.icelandair.com',
    'www.spotifyjobs.com', 'www.ericsson.com', 'www.nokia.fi', 'www.volvocars.com',
    'www.scania.se', 'www.electrolux.com', 'www.husqvarna.com', 'www.stiga.com',
    'www.lego.com', 'www.maersktankers.com', 'www.novonordisk.com',
    'www.carlsberg.com', 'www.arla.com', 'www.vestas.com', 'www.grundfos.com',
    'www.swedbankrobur.se', 'www.storebrand.no', 'www.tryg.dk',
    'www.swedishnumbers.com', 'www.lhv.ee', 'www.swedbank.lt', 'www.seb.lv',
    'www.telia.lt', 'www.bite.lt', 'www.tele2.lv', 'www.delfi.lt',
    'www.delfi.lv', 'www.postimees.ee', 'www.err.ee', 'www.e-resident.gov.ee',
)

# ---------------------------------------------------------------------------
# Central and eastern Europe
# ---------------------------------------------------------------------------
add(
    'www.allegro.pl', 'www.olx.pl', 'www.ceneo.pl', 'www.empik.com',
    'www.mbank.pl', 'www.pkobp.pl', 'www.ing.pl', 'www.santander.pl',
    'www.onet.pl', 'www.wp.pl', 'www.interia.pl', 'www.gazeta.pl',
    'www.tvn24.pl', 'www.orange.pl', 'www.play.pl', 'www.plus.pl',
    'www.cdaction.pl', 'www.cdprojektred.com', 'www.techland.pl',
    'www.seznam.cz', 'www.alza.cz', 'www.mall.cz', 'www.rohlik.cz',
    'www.csob.cz', 'www.kb.cz', 'www.o2.cz', 'www.t-mobile.cz',
    'www.idnes.cz', 'www.novinky.cz', 'www.aktualne.cz',
    'www.azet.sk', 'www.zoznam.sk', 'www.alza.sk', 'www.telekom.sk',
    'www.hu.wikipedia.org', 'www.telekom.hu', 'www.otpbank.hu',
    'www.index.hu', 'www.origo.hu', 'www.24.hu', 'www.emag.hu',
    'www.emag.ro', 'www.olx.ro', 'www.digi.ro', 'www.orange.ro',
    'www.bcr.ro', 'www.brd.ro', 'www.digi24.ro', 'www.hotnews.ro',
    'www.mtel.bg', 'www.vivacom.bg', 'www.dnevnik.bg', 'www.dir.bg',
    'www.hrt.hr', 'www.index.hr', 'www.jutarnji.hr', 'www.zagreb.hr',
    'www.rtvslo.si', 'www.24ur.com', 'www.telekom.si', 'www.mimovrste.com',
    'www.blic.rs', 'www.b92.net', 'www.telekom.rs', 'www.kupujemprodajem.com',
    'www.a1.rs', 'www.aik.rs', 'www.nlb.rs',
)

# ---------------------------------------------------------------------------
# Turkey, Israel, Gulf, wider Middle East
# ---------------------------------------------------------------------------
add(
    'www.hepsiburada.com', 'www.trendyol.com', 'www.n11.com', 'www.gittigidiyor.com',
    'www.sahibinden.com', 'www.turkcell.com.tr', 'www.vodafone.com.tr',
    'www.turktelekom.com.tr', 'www.isbank.com.tr', 'www.garantibbva.com.tr',
    'www.akbank.com', 'www.yapikredi.com.tr', 'www.ziraatbank.com.tr',
    'www.hurriyet.com.tr', 'www.milliyet.com.tr', 'www.sabah.com.tr',
    'www.ntv.com.tr', 'www.trthaber.com', 'www.anadoluagency.com',
    'www.getir.com', 'www.yemeksepeti.com', 'www.pegasus.com', 'www.ajet.com',
    'www.migros.com.tr', 'www.a101.com.tr', 'www.bim.com.tr', 'www.teknosa.com',
    'www.vestel.com.tr', 'www.arcelik.com.tr', 'www.beko.com',
    'www.wix.com', 'www.monday.com', 'www.check-point.com', 'www.cyberark.com',
    'www.jfrog.com', 'www.elastic.io', 'www.mobileye.com', 'www.teva.co.il',
    'www.bankleumi.co.il', 'www.bankhapoalim.co.il', 'www.ynet.co.il',
    'www.haaretz.com', 'www.jpost.com', 'www.timesofisrael.com',
    'www.weizmann.ac.il', 'www.technion.ac.il', 'www.huji.ac.il', 'www.tau.ac.il',
    'www.emirates.net.ae', 'www.etisalat.ae', 'www.du.ae', 'www.adnoc.ae',
    'www.emiratesnbd.com', 'www.mashreqbank.com', 'www.dubai.ae',
    'www.thenationalnews.com', 'www.khaleejtimes.com', 'www.gulfnews.com',
    'www.aramco.com', 'www.stc.com.sa', 'www.mobily.com.sa', 'www.zain.com',
    'www.alrajhibank.com.sa', 'www.ncb.com.sa', 'www.noon.com', 'www.namshi.com',
    'www.qatarairways.com.qa', 'www.ooredoo.qa', 'www.aljazeera.com',
    'www.aljazeera.net', 'www.kuwaitairways.com', 'www.zain.com.kw',
    'www.omantel.om', 'www.bahrain.bh', 'www.batelco.com',
)

# ---------------------------------------------------------------------------
# Africa
# ---------------------------------------------------------------------------
add(
    'www.mtn.com', 'www.vodacom.co.za', 'www.telkom.co.za', 'www.rain.co.za',
    'www.standardbank.co.za', 'www.absa.co.za', 'www.fnb.co.za',
    'www.nedbank.co.za', 'www.capitecbank.co.za', 'www.discovery.co.za',
    'www.takealot.com', 'www.superbalist.com', 'www.makro.co.za',
    'www.news24.com', 'www.iol.co.za', 'www.timeslive.co.za', 'www.ewn.co.za',
    'www.sabc.co.za', 'www.uct.ac.za', 'www.wits.ac.za', 'www.up.ac.za',
    'www.sun.ac.za', 'www.safaricom.co.ke', 'www.equitybank.co.ke',
    'www.kcbgroup.com', 'www.nation.africa', 'www.standardmedia.co.ke',
    'www.jumia.com', 'www.konga.com', 'www.gtbank.com', 'www.zenithbank.com',
    'www.accessbankplc.com', 'www.firstbanknigeria.com', 'www.flutterwave.com',
    'www.paystack.com', 'www.punchng.com', 'www.vanguardngr.com',
    'www.premiumtimesng.com', 'www.mtn.ng', 'www.airtel.com.ng',
    'www.orange.eg', 'www.vodafone.com.eg', 'www.etisalat.eg',
    'www.ahram.org.eg', 'www.almasryalyoum.com', 'www.aucegypt.edu',
    'www.maroctelecom.ma', 'www.inwi.ma', 'www.attijariwafabank.com',
    'www.hespress.com', 'www.le360.ma', 'www.ooredoo.dz', 'www.djezzy.dz',
    'www.tunisietelecom.tn', 'www.ooredoo.tn',
)

# ---------------------------------------------------------------------------
# South and south-east Asia, more of east Asia
# ---------------------------------------------------------------------------
add(
    'www.hdfcbank.com', 'www.icicibank.com', 'www.axisbank.com', 'www.sbi.co.in',
    'www.kotak.com', 'www.phonepe.com', 'www.razorpay.com', 'www.zerodha.com',
    'www.groww.in', 'www.cred.club', 'www.meesho.com', 'www.nykaa.com',
    'www.bigbasket.com', 'www.bookmyshow.com', 'www.makemytrip.com',
    'www.oyorooms.com', 'www.olacabs.com', 'www.uber.com', 'www.rapido.bike',
    'www.tcs.com', 'www.infosys.com', 'www.wipro.com', 'www.hcltech.com',
    'www.techmahindra.com', 'www.reliance.com', 'www.tatamotors.com',
    'www.mahindra.com', 'www.bajajauto.com', 'www.heromotocorp.com',
    'www.indiatoday.in', 'www.hindustantimes.com', 'www.livemint.com',
    'www.economictimes.com', 'www.business-standard.com', 'www.scroll.in',
    'www.iitb.ac.in', 'www.iitd.ac.in', 'www.iitm.ac.in', 'www.iisc.ac.in',
    'www.bkash.com', 'www.grameenphone.com', 'www.robi.com.bd',
    'www.prothomalo.com', 'www.thedailystar.net', 'www.buet.ac.bd',
    'www.jazz.com.pk', 'www.telenor.com.pk', 'www.hbl.com', 'www.daraz.pk',
    'www.dawn.com', 'www.geo.tv', 'www.nust.edu.pk', 'www.lums.edu.pk',
    'www.dialog.lk', 'www.slt.lk', 'www.dailymirror.lk',
    'www.viettel.com.vn', 'www.vnpt.com.vn', 'www.mobifone.vn',
    'www.vnexpress.net', 'www.tuoitre.vn', 'www.thanhnien.vn',
    'www.tiki.vn', 'www.sendo.vn', 'www.vietcombank.com.vn',
    'www.ais.co.th', 'www.truecorp.co.th', 'www.dtac.co.th',
    'www.kasikornbank.com', 'www.scb.co.th', 'www.bangkokpost.com',
    'www.thairath.co.th', 'www.chula.ac.th', 'www.mahidol.ac.th',
    'www.singtel.com', 'www.starhub.com', 'www.dbs.com.sg', 'www.ocbc.com',
    'www.uob.com.sg', 'www.straitstimes.com', 'www.channelnewsasia.com',
    'www.maybank.com', 'www.cimb.com', 'www.maxis.com.my', 'www.digi.com.my',
    'www.thestar.com.my', 'www.astro.com.my', 'www.um.edu.my',
    'www.globe.com.ph', 'www.smart.com.ph', 'www.bdo.com.ph',
    'www.inquirer.net', 'www.rappler.com', 'www.gmanetwork.com',
    'www.telkomsel.com', 'www.indosatooredoo.com', 'www.xl.co.id',
    'www.kompas.com', 'www.detik.com', 'www.bca.co.id', 'www.bri.co.id',
    'www.ui.ac.id', 'www.itb.ac.id',
)

# ---------------------------------------------------------------------------
# Latin America
# ---------------------------------------------------------------------------
add(
    'www.claro.com.br', 'www.vivo.com.br', 'www.tim.com.br', 'www.oi.com.br',
    'www.santander.com.br', 'www.caixa.gov.br', 'www.bb.com.br',
    'www.folha.uol.com.br', 'www.estadao.com.br', 'www.g1.globo.com',
    'www.terra.com.br', 'www.ig.com.br', 'www.usp.br', 'www.unicamp.br',
    'www.ufrj.br', 'www.ufmg.br', 'www.petrobras.com.br', 'www.embraer.com',
    'www.natura.com.br', 'www.ambev.com.br', 'www.ifood.com.br',
    'www.rappi.com', 'www.pedidosya.com', 'www.despegar.com',
    'www.telcel.com', 'www.att.com.mx', 'www.movistar.com.mx',
    'www.bbva.mx', 'www.banorte.com', 'www.banamex.com', 'www.liverpool.com.mx',
    'www.elektra.com.mx', 'www.milenio.com', 'www.excelsior.com.mx',
    'www.unam.mx', 'www.tec.mx', 'www.ipn.mx',
    'www.entel.cl', 'www.movistar.cl', 'www.wom.cl', 'www.bancochile.cl',
    'www.santander.cl', 'www.falabella.com', 'www.emol.com', 'www.latercera.com',
    'www.uchile.cl', 'www.puc.cl', 'www.usach.cl',
    'www.personal.com.ar', 'www.movistar.com.ar', 'www.claro.com.ar',
    'www.lanacion.com.ar', 'www.infobae.com', 'www.pagina12.com.ar',
    'www.uba.ar', 'www.utn.edu.ar', 'www.bancogalicia.com',
    'www.bancolombia.com', 'www.davivienda.com', 'www.eltiempo.com',
    'www.semana.com', 'www.unal.edu.co', 'www.uniandes.edu.co',
    'www.bcp.com.pe', 'www.interbank.pe', 'www.elcomercio.pe', 'www.pucp.edu.pe',
)

# ---------------------------------------------------------------------------
# Sport, aviation, hospitality
# ---------------------------------------------------------------------------
add(
    'www.realmadrid.com', 'www.fcbarcelona.com', 'www.manutd.com',
    'www.liverpoolfc.com', 'www.arsenal.com', 'www.chelseafc.com',
    'www.mancity.com', 'www.tottenhamhotspur.com', 'www.fcbayern.com',
    'www.bvb.de', 'www.juventus.com', 'www.acmilan.com', 'www.inter.it',
    'www.psg.fr', 'www.ajax.nl', 'www.benfica.pt', 'www.fcporto.pt',
    'www.premierleague.com', 'www.bundesliga.com', 'www.laliga.com',
    'www.legaseriea.it', 'www.ligue1.com', 'www.eredivisie.nl',
    'www.atptour.com', 'www.wtatennis.com', 'www.wimbledon.com',
    'www.rolandgarros.com', 'www.usopen.org', 'www.ausopen.com',
    'www.pgatour.com', 'www.europeantour.com', 'www.motogp.com',
    'www.wrc.com', 'www.uci.org', 'www.letour.fr', 'www.giroditalia.it',
    'www.worldrugby.org', 'www.icc-cricket.com', 'www.bcci.tv',
    'www.olympic.org', 'www.paralympic.org', 'www.fina.org', 'www.iaaf.org',
    'www.worldathletics.org', 'www.fiba.basketball', 'www.ihf.info',
    'www.aa.com', 'www.delta.com', 'www.united.com', 'www.southwest.com',
    'www.jetblue.com', 'www.alaskaair.com', 'www.aircanada.com',
    'www.westjet.com', 'www.iberia.com', 'www.vueling.com', 'www.tap.pt',
    'www.aegeanair.com', 'www.lot.com', 'www.wizzair.com', 'www.easyjet.com',
    'www.ryanair.ie', 'www.finnair.fi', 'www.airbaltic.com',
    'www.singaporeair.com', 'www.cathaypacific.com', 'www.ana.co.jp',
    'www.jal.co.jp', 'www.koreanair.com', 'www.flyasiana.com',
    'www.airindia.com', 'www.indigo.in', 'www.airnewzealand.co.nz',
    'www.qantas.com', 'www.virginaustralia.com', 'www.latamairlines.com',
    'www.marriott.com', 'www.hilton.com', 'www.hyatt.com', 'www.ihg.com',
    'www.accor.com', 'www.radissonhotels.com', 'www.wyndhamhotels.com',
    'www.melia.com', 'www.nh-hotels.com', 'www.motel-one.com',
    'www.hostelworld.com', 'www.agoda.com', 'www.trip.com', 'www.kayak.com',
    'www.trivago.com', 'www.hotels.com', 'www.opodo.com', 'www.edreams.com',
)

# ---------------------------------------------------------------------------
# Government and intergovernmental
# ---------------------------------------------------------------------------
add(
    'www.gov.uk', 'www.canada.ca', 'www.australia.gov.au', 'www.govt.nz',
    'www.gouvernement.fr', 'www.service-public.fr', 'www.gob.es',
    'www.governo.it', 'www.rijksoverheid.nl', 'www.belgium.be',
    'www.admin.ch', 'www.oesterreich.gv.at', 'www.regeringen.se',
    'www.regjeringen.no', 'www.stm.fi', 'www.regeringen.dk',
    'www.usa.gov', 'www.whitehouse.gov', 'www.state.gov', 'www.treasury.gov',
    'www.energy.gov', 'www.nsf.gov', 'www.usgs.gov', 'www.census.gov',
    'www.loc.gov', 'www.archives.gov', 'www.gpo.gov', 'www.uspto.gov',
    'www.faa.gov', 'www.fcc.gov', 'www.ftc.gov', 'www.sec.gov',
    'www.nist.gov', 'www.epa.gov', 'www.ed.gov', 'www.dhs.gov',
    'www.worldbank.org', 'www.imf.org', 'www.wto.org', 'www.oecd.org',
    'www.unesco.org', 'www.unicef.org', 'www.unhcr.org', 'www.undp.org',
    'www.fao.org', 'www.ilo.org', 'www.wipo.int', 'www.itu.int',
    'www.wmo.int', 'www.iaea.org', 'www.nato.int', 'www.coe.int',
    'www.echr.coe.int', 'www.europarl.europa.eu', 'www.consilium.europa.eu',
    'www.eba.europa.eu', 'www.esma.europa.eu', 'www.eea.europa.eu',
    'www.efsa.europa.eu', 'www.ema.europa.eu', 'www.enisa.europa.eu',
    'www.eurofound.europa.eu', 'www.eib.org', 'www.ebrd.com',
    'www.adb.org', 'www.afdb.org', 'www.iadb.org', 'www.icrc.org',
    'www.ifrc.org', 'www.msf.org', 'www.amnesty.org', 'www.hrw.org',
    'www.greenpeace.org', 'www.wwf.org', 'www.redcross.org',
)

# ---------------------------------------------------------------------------
# Open-source projects and technical foundations
# ---------------------------------------------------------------------------
add(
    'www.gnu.org', 'www.fsf.org', 'www.linuxfoundation.org', 'www.opensource.org',
    'www.cncf.io', 'www.openssl.org', 'www.libressl.org', 'www.wolfssl.com',
    'curl.se', 'www.openssh.com', 'www.wireguard.com', 'openvpn.net',
    'www.strongswan.org', 'www.freeradius.org', 'www.isc.org', 'www.bind9.net',
    'www.powerdns.com', 'nlnetlabs.nl', 'www.unbound.net', 'www.haproxy.org',
    'varnish-cache.org', 'traefik.io', 'envoyproxy.io', 'istio.io',
    'linkerd.io', 'www.consul.io', 'www.vaultproject.io', 'www.nomadproject.io',
    'www.packer.io', 'www.vagrantup.com', 'www.ansible.com', 'puppet.com',
    'www.chef.io', 'saltproject.io', 'www.jenkins.io', 'www.sonarqube.org',
    'www.sonarsource.com', 'gradle.org', 'maven.apache.org', 'ant.apache.org',
    'www.scala-lang.org', 'kotlinlang.org', 'clojure.org', 'elixir-lang.org',
    'www.erlang.org', 'www.haskell.org', 'ocaml.org', 'fsharp.org',
    'julialang.org', 'www.r-project.org', 'cran.r-project.org', 'posit.co',
    'www.perl.org', 'metacpan.org', 'www.php.net', 'www.lua.org',
    'www.ruby-lang.org', 'rubyonrails.org', 'laravel.com', 'symfony.com',
    'www.djangoproject.com', 'flask.palletsprojects.com', 'fastapi.tiangolo.com',
    'numpy.org', 'scipy.org', 'pandas.pydata.org', 'matplotlib.org',
    'scikit-learn.org', 'jupyter.org', 'ipython.org', 'conda.io',
    'anaconda.org', 'www.sqlite.org', 'duckdb.org', 'clickhouse.com',
    'www.timescale.com', 'www.cockroachlabs.com', 'planetscale.com',
    'neo4j.com', 'cassandra.apache.org', 'couchdb.apache.org',
    'www.influxdata.com', 'min.io', 'ceph.io', 'www.gluster.org',
    'www.zfsonlinux.org', 'www.proxmox.com', 'www.qemu.org', 'libvirt.org',
    'www.linux-kvm.org', 'www.xenproject.org', 'www.openstack.org',
    'www.freebsd.org', 'www.openbsd.org', 'www.netbsd.org', 'www.dragonflybsd.org',
    'www.gentoo.org', 'www.slackware.com', 'www.devuan.org', 'alpinelinux.org',
    'www.voidlinux.org', 'nixos.org', 'guix.gnu.org', 'endeavouros.com',
    'manjaro.org', 'linuxmint.com', 'elementary.io', 'zorin.com',
    'popos.org', 'kali.org', 'www.parrotsec.org', 'tails.net',
    'www.qubes-os.org', 'www.whonix.org', 'www.raspberrypi.com',
    'www.arduino.cc', 'micropython.org', 'platformio.org', 'zephyrproject.org',
    'www.freertos.org', 'riot-os.org', 'www.contiki-ng.org',
    'www.blender.org', 'www.gimp.org', 'inkscape.org', 'krita.org',
    'www.audacityteam.org', 'www.ardour.org', 'obsproject.com',
    'ffmpeg.org', 'www.videohelp.com', 'handbrake.fr', 'mpv.io',
    'www.kodi.tv', 'jellyfin.org', 'plex.tv', 'emby.media',
    'nextcloud.com', 'owncloud.com', 'syncthing.net', 'rclone.org',
    'restic.net', 'www.borgbackup.org', 'duplicity.us', 'www.veeam.com',
    'matrix.org', 'element.io', 'xmpp.org', 'prosody.im', 'jitsi.org',
    'meet.jit.si', 'bigbluebutton.org', 'mattermost.com', 'rocket.chat',
    'joinmastodon.org', 'misskey-hub.net', 'lemmy.ml', 'peertube.tv',
    'joinpeertube.org', 'writefreely.org', 'ghost.org', 'wordpress.org',
    'joomla.org', 'www.drupal.org', 'typo3.org', 'craftcms.com',
    'strapi.io', 'directus.io', 'payloadcms.com', 'sanity.io',
    'www.prisma.io', 'sequelize.org', 'typeorm.io', 'knexjs.org',
    'expressjs.com', 'koajs.com', 'fastify.dev', 'nestjs.com',
    'deno.com', 'bun.sh', 'pnpm.io', 'yarnpkg.com', 'turbo.build',
    'nx.dev', 'lerna.js.org', 'rollupjs.org', 'parceljs.org', 'esbuild.github.io',
    'swc.rs', 'biomejs.dev', 'stylelint.io', 'postcss.org',
    'storybook.js.org', 'vitest.dev', 'mochajs.org', 'jasmine.github.io',
    'karma-runner.github.io', 'testcafe.io', 'puppeteer.dev',
    'www.chromatic.com', 'www.netlify.app', 'surge.sh', 'zeabur.com',
)

# ---------------------------------------------------------------------------
# Combinatorial infrastructure subdomains over large apex domains.
#
# Most of these will not exist; DNS failures are cheap for the validator to
# discard, and each one that resolves is the kind of quiet endpoint the ranking
# puts first.
# ---------------------------------------------------------------------------
INFRA_PREFIXES = ('api', 'cdn', 'static', 'assets', 'img', 'media', 'files', 'edge')

APEXES = (
    'shopify.com', 'squarespace.com', 'wix.com', 'webflow.com', 'bigcommerce.com',
    'woocommerce.com', 'magento.com', 'prestashop.com', 'ecwid.com',
    'zoominfo.com', 'crunchbase.com', 'producthunt.com', 'angel.co',
    'ycombinator.com', 'techstars.com', 'sequoiacap.com', 'a16z.com',
    'stripe.com', 'square.com', 'adyen.com', 'checkout.com', 'mollie.com',
    'gocardless.com', 'plaid.com', 'marqeta.com', 'brex.com', 'ramp.com',
    'okta.com', 'auth0.com', 'onelogin.com', 'duo.com', 'jumpcloud.com',
    'datadoghq.com', 'newrelic.com', 'dynatrace.com', 'splunk.com',
    'sumologic.com', 'logz.io', 'honeycomb.io', 'lightstep.com',
    'pagerduty.com', 'opsgenie.com', 'statuspage.io', 'atlassian.com',
    'zendesk.com', 'freshworks.com', 'helpscout.com', 'front.com',
    'twilio.com', 'vonage.com', 'bandwidth.com', 'sinch.com', 'messagebird.com',
    'sendgrid.com', 'mailgun.com', 'postmarkapp.com', 'sparkpost.com',
    'algolia.com', 'elastic.co', 'meilisearch.com', 'typesense.org',
    'contentful.com', 'prismic.io', 'storyblok.com', 'hygraph.com',
    'cloudinary.com', 'imgix.com', 'uploadcare.com', 'filestack.com',
    'mux.com', 'jwplayer.com', 'brightcove.com', 'kaltura.com', 'wistia.com',
    'vimeo.com', 'dailymotion.com', 'rumble.com', 'odysee.com',
    'unity3d.com', 'unrealengine.com', 'godotengine.org', 'construct.net',
    'itch.io', 'gamejolt.com', 'newgrounds.com', 'kongregate.com',
    'coursera.org', 'edx.org', 'futurelearn.com', 'openlearning.com',
    'duolingo.com', 'babbel.com', 'busuu.com', 'memrise.com',
    'strava.com', 'garmin.com', 'polar.com', 'suunto.com', 'wahoofitness.com',
    'myfitnesspal.com', 'fitbit.com', 'whoop.com', 'oura.com', 'peloton.com',
    'notion.so', 'obsidian.md', 'roamresearch.com', 'logseq.com', 'craft.do',
    'todoist.com', 'ticktick.com', 'things.app', 'omnigroup.com',
    'miro.com', 'mural.co', 'lucidchart.com', 'diagrams.net', 'excalidraw.com',
    'figma.com', 'sketch.com', 'invisionapp.com', 'framer.com', 'protopie.io',
    'unsplash.com', 'pexels.com', 'pixabay.com', 'freepik.com', 'envato.com',
    'creativemarket.com', 'dribbble.com', 'behance.net', 'artstation.com',
    'deviantart.com', 'pixiv.net', 'newgrounds.com',
)


def main():
    for apex in APEXES:
        for prefix in INFRA_PREFIXES:
            CANDIDATES.append(f'{prefix}.{apex}')
        CANDIDATES.append(f'www.{apex}')

    seen = set()
    for name in CANDIDATES:
        name = name.strip().lower()
        if name and name not in seen and '.' in name:
            seen.add(name)
            print(name)


if __name__ == '__main__':
    main()
