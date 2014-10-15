# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from pprint import pprint, pformat
import redis
import tornadio2

from django.conf import settings
from django.http import Http404
from django.views.generic.base import TemplateView

from apps.websockets.redisfuncs import RedCache


class RedisView(TemplateView):
    template_name = "redis.html"
    default_redis = redis.Redis()

    def get(self, request, *args, **kwargs):
        if not all((request.user.is_superuser, )): #request.user.is_authenticated(),
            raise Http404

        return super(RedisView, self).get(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs):        
        context = super(RedisView, self).get_context_data(**kwargs)

        context['dbs'] = get_all(self.default_redis)
        context['default_status'] = pretty( get_redis_info(self.default_redis) )

        context['load_stats'] = pformat(RedCache().get('load_stat'))

        # print context['load_stats']
        # print dir(tornadio2.stats)
        # StatsCollector

        return context


def get_all(red):    
    results = []
    for database in filter(lambda x: x.startswith('db'), get_redis_info(red).iterkeys()):
        result = {}
        result['name'] = database
        result['name_redis'] = database.replace('db', '')

        red = redis.Redis(db=int(result['name_redis']))        
        result['keys_values'] = [(x, get_redis_value(red, x)) for x in get_redis_keys(red)]

        # result['load_stats'] = get_redis_value(red, 'cache|load_stat')


        results.append(result)
    return results

def pretty(obj):
    return pformat(obj, indent=4, width=128, depth=8)

def get_redis_info(red):
    return red.info()

def get_redis_keys(red):
    #return iter(red.keys(pattern='*'))    
    return red.keys(pattern='*')

def get_dbs(red):
    get_redis_info(red)

def get_redis_value(red, key):    
    try:
        return repr(red.get(key))
    except Exception, e:
        return "!!! {0}".format(e)