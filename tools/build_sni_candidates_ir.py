#!/usr/bin/env python3
"""
Iranian SNI candidates for Reality.

Why a separate list: an Iranian SNI is only useful if the Reality server abroad
can still complete a TLS handshake with it, and a good many Iranian sites refuse
connections from foreign IP space outright. That filter cannot be guessed - it
has to be measured from the server that will host the inbounds, which is what
validate_sni.py does.

Ordering the domestic list also works differently. The whole point of a domestic
SNI is that it looks domestic, so the usual "prefer quiet API endpoints" bias
matters less here than simply being a large, well provisioned site that plausibly
carries a lot of traffic.

Output: one hostname per line on stdout.
"""

CANDIDATES = []


def add(*names):
    CANDIDATES.extend(names)


# ---------------------------------------------------------------------------
# Iranian CDN and cloud infrastructure - the best provisioned targets available
# ---------------------------------------------------------------------------
add(
    'www.arvancloud.ir', 'arvancloud.ir', 'panel.arvancloud.ir',
    'www.arvancloud.com', 'arvancloud.com', 'napi.arvancloud.ir',
    'cdn.arvancloud.ir', 's3.ir-thr-at1.arvanstorage.ir',
    's3.ir-tbz-sh1.arvanstorage.ir', 'arvanstorage.ir',
    'www.parspack.com', 'parspack.com', 'my.parspack.com',
    'www.iranserver.com', 'iranserver.com', 'www.mizban.com',
    'www.hostiran.net', 'www.abrarvan.com', 'www.abrha.com',
    'www.zarinserver.com', 'www.novinhost.org', 'www.faraso.org',
    'www.dorsa.host', 'www.sabaidc.com', 'www.afranet.com',
    'www.shatel.ir', 'my.shatel.ir', 'www.shatelland.com',
    'www.pishgaman.net', 'www.asiatech.ir', 'www.parsonline.com',
    'www.datak.ir', 'www.respina.net', 'www.fanava.com',
    'www.mobinnet.ir', 'www.hiweb.ir', 'www.tci.ir',
    'www.irancell.ir', 'www.mci.ir', 'my.mci.ir', 'www.rightel.ir',
    'www.samantel.ir', 'www.shahrad.ir',
)

# ---------------------------------------------------------------------------
# Large consumer platforms
# ---------------------------------------------------------------------------
add(
    'www.digikala.com', 'digikala.com', 'api.digikala.com', 'dkstatics-public.digikala.com',
    'www.torob.com', 'torob.com', 'api.torob.com',
    'www.basalam.com', 'basalam.com', 'statics.basalam.com',
    'www.divar.ir', 'divar.ir', 'api.divar.ir', 's100.divarcdn.com',
    'www.sheypoor.com', 'sheypoor.com', 'www.emalls.ir',
    'snapp.ir', 'www.snapp.ir', 'app.snapp.taxi', 'snapp.market',
    'www.snappfood.ir', 'snappfood.ir', 'www.snapptrip.com',
    'www.snappdoctor.com', 'www.snappshop.ir', 'www.snapppay.ir',
    'tapsi.ir', 'www.tapsi.ir', 'api.tapsi.ir',
    'www.alibaba.ir', 'alibaba.ir', 'www.flytoday.ir', 'www.safarmarket.com',
    'www.mrbilit.com', 'www.ghasedak24.com', 'www.eligasht.com',
    'www.okala.com', 'www.ofoghkourosh.com', 'www.hyperstar.ir',
    'www.digistyle.com', 'www.modiseh.com', 'www.banimode.com',
    'www.zoodfood.com', 'www.chilivery.com', 'www.reyhoon.com',
)

# ---------------------------------------------------------------------------
# Media, video and music
# ---------------------------------------------------------------------------
add(
    'www.aparat.com', 'aparat.com', 'static.cdn.asset.aparat.com',
    'www.filimo.com', 'filimo.com', 'www.namava.ir', 'namava.ir',
    'www.telewebion.com', 'telewebion.com', 'www.lenzor.com',
    'www.tamashakhoneh.ir', 'www.iranseda.ir', 'www.irib.ir',
    'www.tva.ir', 'www.beeptunes.com', 'www.melodify.app',
    'www.radiojavan.com', 'www.navaar.ir', 'www.fidibo.com',
    'www.taaghche.com', 'www.ketabrah.ir', 'www.30book.com',
)

# ---------------------------------------------------------------------------
# News agencies and newspapers
# ---------------------------------------------------------------------------
add(
    'www.irna.ir', 'irna.ir', 'www.isna.ir', 'isna.ir',
    'www.mehrnews.com', 'mehrnews.com', 'www.tasnimnews.com', 'tasnimnews.com',
    'www.farsnews.ir', 'farsnews.ir', 'www.khabaronline.ir', 'khabaronline.ir',
    'www.yjc.ir', 'www.iribnews.ir', 'www.entekhab.ir', 'www.tabnak.ir',
    'www.asriran.com', 'www.alef.ir', 'www.jamejamonline.ir',
    'www.hamshahrionline.ir', 'www.donya-e-eqtesad.com', 'www.eghtesadnews.com',
    'www.tejaratnews.com', 'www.ecoiran.com', 'www.zoomit.ir', 'zoomit.ir',
    'www.digiato.com', 'digiato.com', 'www.shahrsakhtafzar.com',
    'www.varzesh3.com', 'varzesh3.com', 'www.footballi.net',
    'www.tarafdari.com', 'www.90tv.ir', 'www.mizanonline.ir',
    'www.borna.news', 'www.ilna.ir', 'www.rokna.net', 'www.fardanews.com',
)

# ---------------------------------------------------------------------------
# Banking and payment
# ---------------------------------------------------------------------------
add(
    'www.bmi.ir', 'bmi.ir', 'ib.bmi.ir', 'www.bankmellat.ir', 'bankmellat.ir',
    'www.tejaratbank.ir', 'www.bsi.ir', 'www.sb24.ir', 'www.enbank.ir',
    'www.bpi.ir', 'www.bankpasargad.com', 'www.bank-day.ir',
    'www.parsian-bank.ir', 'www.sinabank.ir', 'www.ansarbank.com',
    'www.refah-bank.ir', 'www.postbank.ir', 'www.bankmaskan.ir',
    'www.bki.ir', 'www.karafarinbank.ir', 'www.middleeastbank.ir',
    'www.shaparak.ir', 'www.sep.ir', 'sep.shaparak.ir', 'www.behpardakht.com',
    'www.pep.co.ir', 'www.zarinpal.com', 'zarinpal.com', 'api.zarinpal.com',
    'www.idpay.ir', 'www.nextpay.org', 'www.payping.ir', 'www.zibal.ir',
    'www.vandar.io', 'www.jibit.ir', 'www.finnotech.ir',
    'www.tgju.org', 'tgju.org', 'www.tsetmc.com', 'www.codal.ir',
    'www.rahavard365.com', 'www.sahamyab.com', 'www.mabnadp.com',
)

# ---------------------------------------------------------------------------
# App stores, tech and developer services
# ---------------------------------------------------------------------------
add(
    'cafebazaar.ir', 'www.cafebazaar.ir', 'api.cafebazaar.ir',
    'www.myket.ir', 'myket.ir', 'www.sibapp.com', 'www.sibche.com',
    'www.iranapps.ir', 'www.charkhoneh.com',
    'www.kavenegar.com', 'www.ghasedak.io', 'www.smsir.com',
    'www.melipayamak.com', 'www.raygan.ir', 'www.sms.ir',
    'www.liara.ir', 'liara.ir', 'www.darkube.app', 'www.cloudzy.com',
    'www.iranrepo.ir', 'mirror.iranrepo.ir', 'repo.iut.ac.ir',
    'mirror.aminidc.com', 'mirror.faraso.org', 'debian.asis.io',
    'www.quera.org', 'quera.org', 'www.faradars.org', 'faradars.org',
    'www.maktabkhooneh.org', 'maktabkhooneh.org', 'www.sokanacademy.com',
    'www.roocket.ir', 'www.jadi.net', 'www.virgool.io', 'virgool.io',
    'www.jobinja.ir', 'jobinja.ir', 'www.jobvision.ir', 'www.irantalent.com',
    'www.karboom.io', 'www.quera.ir',
)

# ---------------------------------------------------------------------------
# Government, public sector and utilities
# ---------------------------------------------------------------------------
add(
    'www.iran.ir', 'www.president.ir', 'www.mfa.gov.ir', 'www.dolat.ir',
    'www.mcls.gov.ir', 'www.mefa.ir', 'www.moe.gov.ir', 'www.mop.ir',
    'www.moh.gov.ir', 'behdasht.gov.ir', 'www.msrt.ir', 'www.medu.ir',
    'www.sabteahval.ir', 'www.ssaa.ir', 'www.tamin.ir', 'www.inta.gov.ir',
    'www.irica.gov.ir', 'www.cbi.ir', 'cbi.ir', 'www.amar.org.ir',
    'www.post.ir', 'www.rmto.ir', 'www.raja.ir', 'www.airport.ir',
    'www.iranair.com', 'www.mahan.aero', 'www.qeshm-air.com',
    'www.tavanir.org.ir', 'www.nigc.ir', 'www.nioc.ir', 'www.abfa.ir',
    'www.iranicm.ir', 'www.nezam.org', 'www.irandoc.ac.ir',
    'www.nlai.ir', 'www.ical.ir', 'www.rc.majlis.ir',
    'www.mydocument.ir', 'www.epolice.ir', 'www.adliran.ir',
)

# ---------------------------------------------------------------------------
# Universities and research
# ---------------------------------------------------------------------------
add(
    'www.ut.ac.ir', 'ut.ac.ir', 'www.sharif.ir', 'sharif.ir', 'www.sharif.edu',
    'www.aut.ac.ir', 'aut.ac.ir', 'www.modares.ac.ir', 'www.iust.ac.ir',
    'www.sbu.ac.ir', 'www.shirazu.ac.ir', 'www.um.ac.ir', 'www.tabrizu.ac.ir',
    'www.iut.ac.ir', 'www.kntu.ac.ir', 'www.uk.ac.ir', 'www.guilan.ac.ir',
    'www.urmia.ac.ir', 'www.razi.ac.ir', 'www.yazd.ac.ir', 'www.uma.ac.ir',
    'www.semnan.ac.ir', 'www.basu.ac.ir', 'www.shahroodut.ac.ir',
    'www.iau.ir', 'www.pnu.ac.ir', 'www.uast.ac.ir', 'www.sanjesh.org',
    'www.konkur.in', 'www.civilica.com', 'civilica.com', 'www.sid.ir',
    'www.magiran.com', 'www.noormags.ir', 'www.ensani.ir', 'www.irandoc.ir',
    'www.ricest.ac.ir', 'www.iranjournals.nlai.ir',
)

# ---------------------------------------------------------------------------
# Insurance, industry, retail chains
# ---------------------------------------------------------------------------
add(
    'www.iraninsurance.ir', 'www.alborzinsurance.ir', 'www.pasargadinsurance.ir',
    'www.parsianinsurance.ir', 'www.dayins.com', 'www.mellatinsurance.com',
    'www.saipacorp.com', 'www.ikco.ir', 'www.bahman.ir', 'www.kerman-motor.com',
    'www.mvmco.ir', 'www.modirankhodro.com', 'www.snowa.ir',
    'www.emersun.co', 'www.pakshoo.com', 'www.golrang.com',
    'www.kalleh.com', 'www.mihan.net', 'www.damdaran.ir',
    'www.zarmacaron.com', 'www.minoo.ir', 'www.shirinasal.com',
    'www.refah.ir', 'www.shahrvand.ir', 'www.janbo.net', 'www.afoghkourosh.com',
    'www.digikalajet.com', 'www.technolife.ir', 'www.mobit.ir',
    'www.hamrahtel.com', 'www.mobile.ir', 'www.zoodrasan.com',
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
