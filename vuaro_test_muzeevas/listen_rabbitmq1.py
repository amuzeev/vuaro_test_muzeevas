#!/usr/bin/env python
#!-*- coding: utf-8 -*-

import pika

from .server import handle_delivery

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