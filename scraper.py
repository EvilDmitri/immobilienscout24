# -*- coding: utf-8 -*-
import csv

import logging
import os

from grab.spider import Spider, Task
from grab.tools import html

from grab.tools.logs import default_logging
from hashlib import sha1

from grab import Grab

g = Grab()

default_logging(level=logging.DEBUG)

path = os.path.dirname(os.path.abspath(__file__))

MAIN_LINK = 'http://www.immobilienscout24.de/Suche/S-T/P-{}/Wohnung-Miete/Berlin/Berlin'

THREADS = 2


class Immospider(Spider):
    def __init__(self):
        super(Immospider, self).__init__(thread_number=THREADS, network_try_limit=20)
        self.result_file = csv.writer(open('result.txt', 'w'))
        self.result_file.writerow(['Title', 'Address', 'Wohnungstyp', 'Etage', 'Wohnflaeche', 'Bezugsfrei_ab',
                                  'Zimmer', 'Haustiere', 'Kaltmiete', 'Nebenkosten', 'Heizkosten', 'Gesamtmiete',
                                  'Kaution_o_genossenschaftsanteile'])

    def task_generator(self):

        # Get number of pages
        g.go('http://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin')
        a = g.xpath_list('//select[@class="select font-standard"]')[0]
        pages = len(a.getchildren())

        for number in xrange(10):
        # for number in xrange(pages+1):
            url = MAIN_LINK.format(number)
            yield Task('initial', url=url)

    def task_initial(self, grab, task):
        items = grab.xpath_list('//h5[@class]')
        for item in items:
            link = item.getparent()
            url = 'http://www.immobilienscout24.de' + link.attrib['href']
            self.add_task(Task(name='get_data', url=url))

    def task_get_data(self, grab, task):
        title = grab.doc.select('//h1[@id="expose-title"]')[0].text()
        address = grab.doc.select('//div[@class="address-block"]')[0].text()
        address = ''.join(address.split(' (zur Karte)'))    # garbage text

        wohnungstyp = grab.doc.select('//dd[@class="is24qa-wohnungstyp grid-item three-fifths"]')[0].text()
        etage = grab.doc.select('//dd[@class="is24qa-etage grid-item three-fifths"]')[0].text()
        wohnflaeche = grab.doc.select('//dd[@class="is24qa-wohnflaeche-ca grid-item three-fifths"]')[0].text()
        bezugsfrei_ab = grab.doc.select('//dd[@class="is24qa-bezugsfrei-ab grid-item three-fifths"]')[0].text()
        zimmer = grab.doc.select('//dd[@class="is24qa-zimmer grid-item three-fifths"]')[0].text()
        haustiere = grab.doc.select('//dd[@class="is24qa-haustiere grid-item three-fifths"]')[0].text()
        kaltmiete = grab.doc.select('//dd[@class="is24qa-kaltmiete grid-item three-fifths"]')[0].text()
        nebenkosten = grab.doc.select('//dd[@class="is24qa-nebenkosten grid-item three-fifths"]')[0].text()
        heizkosten = grab.doc.select('//dd[@class="is24qa-heizkosten grid-item three-fifths"]')[0].text()
        gesamtmiete = grab.doc.select('//dd[@class="is24qa-gesamtmiete grid-item three-fifths font-bold"]')[0].text()
        kaution_o_genossenschaftsanteile = grab.doc.select(
            '//dd[@class="is24qa-kaution-o-genossenschaftsanteile is24-ex-spacelink grid-item three-fifths"]')[0].text()

        self.result_file.writerow([title, address, wohnungstyp, etage, wohnflaeche, bezugsfrei_ab, zimmer, haustiere, kaltmiete,
                                  nebenkosten, heizkosten, gesamtmiete, kaution_o_genossenschaftsanteile])


def main():
    bot = Immospider()

    # bot.setup_proxylist(proxy_file='proxy.lst')
    bot.setup_grab(hammer_mode=True)

    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    print bot.render_stats()
    print 'All done'


if __name__ == '__main__':
    print 'Start working'
    default_logging(level=logging.DEBUG)
    main()
