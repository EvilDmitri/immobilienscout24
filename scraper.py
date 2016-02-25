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

    def task_generator(self):

        # Get number of pages
        g.go('http://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin')
        a = g.xpath_list('//select[@class="select font-standard"]')[0]
        pages = len(a.getchildren())

        for number in xrange(pages):
            url = MAIN_LINK.format(number)
            yield Task('initial', url=url)

    def task_initial(self, grab, task):
        items = grab.xpath_list('//h5[@class]')
        for item in items:
            link = item.getparent()
            url = 'http://www.immobilienscout24.de' + link.attrib['href']
            self.add_task(Task(name='get_data', url=url))

    def task_get_data(self, grab, task):
        name = task.image_name
        grab.response.save(name, create_dirs=True)


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
