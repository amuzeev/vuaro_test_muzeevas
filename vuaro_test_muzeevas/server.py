#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import time
import json
import pika

import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver

from  tornado.web import url, Application

from threading import Thread

clients = []

# Create a global channel variable to hold our channel object in
channel = None

# Step #2
def on_connected(connection):
    """Called when we are fully connected to RabbitMQ"""
    # Open a channel
    print 'on_connected'
    connection.channel(on_channel_open)

# Step #3
def on_channel_open(new_channel):
    """Called when our channel has opened"""
    print 'on_channel_open'
    global channel
    channel = new_channel
    channel.queue_declare(queue="completed", durable=True, callback=on_queue_declared)

# Step #4
def on_queue_declared(frame):
    """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
    channel.basic_consume(handle_delivery, queue='completed')
    channel.start_consuming()

# Step #5
def handle_delivery(channel, method, header, body):
    """Called when we receive a message from RabbitMQ"""
    print " [x] Received %r" % (body,)
    for itm in clients:
        itm.write_message(body)


def threaded_rmq():
    parameters = pika.ConnectionParameters(
        host='localhost',
        port=5672
    )
    connection = pika.BlockingConnection(parameters)
    print 'Connected:localhost'
    channel = connection.channel()
    channel.queue_declare(queue="completed", durable=True)
    print 'Consumer ready, on completed'
    channel.basic_consume(handle_delivery, queue="completed", no_ack=True)
    channel.start_consuming()


class WebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print "WebSocket opened"
        #self.application.webSocketsPool.append(self)\
        print [prop for prop in dir(self) if not prop.startswith('_')]
        clients.append(self)

    def on_message(self, message):
        print "WebSocket on_message"

        # db = self.application.db
        # message_dict = json.loads(message)
        # db.chat.insert(message_dict)
        # for key, value in enumerate(self.application.webSocketsPool):
        #     if value != self:
        #         value.ws_connection.write_message(message)

    def on_close(self, message=None):
        print "WebSocket closed"
        clients.remove(self)


if __name__ == '__main__':

    thread = Thread(target=threaded_rmq)
    thread.start()



    application = Application([
        url(r'/websocket', WebSocket),
        ])

    #server = tornado.httpserver.HTTPServer(application)
    #server.listen(8888, address='localhost')

    application.listen(8888, address='localhost')

    try:
        print '-' * 64 + '\n'
        print time.asctime()
        print 'running... press Ctrl+C for exit'

        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:

        tornado.ioloop.IOLoop.instance().stop()