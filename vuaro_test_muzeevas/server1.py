#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import time
import json
import pika
import ast


import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver

from  tornado.web import url, Application


class WebSocket(tornado.websocket.WebSocketHandler):
    user_id = None

    def check_origin(self, origin):
        return True

    def open(self):
        print "WebSocket opened"
        #self.application.webSocketsPool.append(self)\
        #self.application.pc.add_event_listener(self)

    def on_message(self, message):
        if 'user_id' in message:
            msg = ast.literal_eval(message)
            self.set_user_id(msg['user_id'])
            self.application.pc.add_event_listener(self.user_id, self)

    def on_close(self, message=None):
        print "WebSocket closed"
        self.application.pc.remove_event_listener(self.user_id, self)

    def set_user_id(self, user_id):
        self.user_id = user_id






class PikaClient(object):

    def __init__(self, io_loop):
        print('PikaClient: __init__')
        self.io_loop = io_loop

        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None

        #self.event_listeners = set([])
        self.event_listeners = {}


    def connect(self):
        if self.connecting:
            print('PikaClient: Already connecting to RabbitMQ')
            return

        print('PikaClient: Connecting to RabbitMQ')
        self.connecting = True

        parameters = pika.ConnectionParameters(
            host='localhost',
            port=5672
        )

        self.connection = pika.TornadoConnection(parameters,
                                            on_open_callback=self.on_connected)

        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        print('PikaClient: connected to RabbitMQ')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        print('PikaClient: Channel open, Declaring queue')
        self.channel = channel
        self.channel.queue_declare(callback=self.on_queue_declared, queue="completed", durable=True)
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues

    def on_queue_declared(self, frame):
        self.channel.basic_consume(self.on_message, queue="completed", no_ack=True)
        print('PikaClient: Channel open, queue_declared, channel consumed')

    def on_closed(self, connection):
        print('PikaClient: rabbit connection closed')
        self.io_loop.stop()

    def on_message(self, channel, method, header, body):

        self.notify_listeners(channel, body)

    def notify_listeners(self, channel, event_obj):
        event_json = ast.literal_eval(event_obj)

        # for listener in self.event_listeners:
        #     listener.write_message(event_json)
        #     print('PikaClient: notified %s' % repr(listener))
        #

        try:
            listener = self.event_listeners[event_json['user_id']]
            listener.write_message(event_json['body'])
        except KeyError:
            pass

    def add_event_listener(self, user_id, listener):
        self.event_listeners[user_id] = listener
        print('PikaClient: listener with id %s added' % user_id)

    def remove_event_listener(self, user_id, listener):
        # try:
        #     self.event_listeners.remove(listener)
        #     print('PikaClient: listener %s removed' % repr(listener))
        # except KeyError:
        #     pass
        if user_id in self.event_listeners: del self.event_listeners[user_id]
        print('PikaClient: listener with id %s removed' % user_id)

application = Application([
    url(r'/websocket', WebSocket),
    ])

if __name__ == '__main__':
    print '-' * 64 + '\n'
    io_loop = tornado.ioloop.IOLoop.instance()

    # PikaClient is our rabbitmq consumer

    print 'Creating PikaClient'
    pc = PikaClient(io_loop)
    application.pc = pc
    print 'Connecting...'
    application.pc.connect()

    print 'Connected'

    application.listen(8888, address='localhost')

    try:

        print time.asctime()
        print 'running... press Ctrl+C for exit'
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
