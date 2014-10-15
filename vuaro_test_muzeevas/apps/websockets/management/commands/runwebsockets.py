# -*- encoding: utf-8 -*-

import time

import tornado


from django.conf import settings
from django.core.management.base import NoArgsCommand



class Command(NoArgsCommand):

    """./manage websockets"""

    def handle_noargs(self, **options):
        """settings and run tornado app"""

        router = tornadio.TornadioRouter(RouterConnection)
        app = tornado.web.Application(
            router.urls,
            debug=settings.DEBUG
        )

        tornadio.SocketServer(app, auto_start=False)
        server = tornado.httpserver.HTTPServer(app)

        server.listen(8989, address='0.0.0.0')

        ioloop_instance = tornado.ioloop.IOLoop.instance()

        stats_collector = tornadio.stats.StatsCollector()
        stats_collector.start(ioloop_instance)

        def callback():
            red = RedCache()
            red.set('load_stat', router.stats.dump())

        interval_ms = 30 * 1000
        scheduler = tornado.ioloop.PeriodicCallback(callback, interval_ms, io_loop=ioloop_instance)
        scheduler.start()

        try:
            print '-' * 64 + '\n'
            print time.asctime()
            print 'running... press Ctrl+C for exit'

            ioloop_instance.start()
        except KeyboardInterrupt:
            ioloop_instance.stop()
