# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps, partial
from itertools import izip, imap
import operator
import redis
import cPickle as pickle
import tornadoredis
import tornado.gen

from redis import Redis, ConnectionPool

from django.conf import settings
from django.utils.importlib import import_module
from django.utils import simplejson as json

from apps.main.utils import memory


# get redis connections options from project settings
_engine = import_module(settings.SESSION_ENGINE)
_host = getattr(settings, 'SESSION_REDIS_HOST', 'localhost')
_port = getattr(settings, 'SESSION_REDIS_PORT', 6379)
_db = getattr(settings, 'SESSION_REDIS_DB', None)
_password = getattr(settings, 'SESSION_REDIS_PASSWORD', None)

# publish custom message to custom channel
# queries_queue = redis.StrictRedis(
#     host=_host,
#     port=_port,
#     db=_db,
#     password=_password
# ).publish


def queries_queue(channel, message):
    backend = redis.StrictRedis(host=_host, port=_port, db=_db, password=_password)
    backend.publish(channel=channel, message=message)
    # дублируем сообщения для центра уведомлений и указываем из какого канала они пришли
    # msg = json.loads(message)
    # msg['channel_name'] = channel
    # msg = json.dumps(msg)
    # backend.publish(channel=settings.CHANNEL_NOTIFICATIONS, message=msg)


def send_to_redis(channel_name, **kwargs):
    """common wrapper for redis queue"""
    kwargs['channel_name'] = str(channel_name)
    queries_queue(str(channel_name), json.dumps(kwargs))


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


def singleton(class_):
    instances = {}
    
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

# @singleton
class RedCache(object):

    """
    Wrapper for redis-py module with cpickle
    """

    def __init__(self, redis=redis.Redis(), prefix='cache|', timeout=60 * 60, pooled=False):
        """ 
        Initialize, possible to reset/setup: default expired time, prefix, number of db

        r = RedCache()
        r = RedCache(redis.Redis(db=9), 'test|', 60*10)
        """
        # if not pooled:
        #     self._redis = redis
        # else:            
        #     self._redis = redis.Redis(db=9, connection_pool=redis.ConnectionPool(max_connections=64))
        self._redis = redis
        self._prefix = prefix
        self._timeout = timeout

    @staticmethod
    def get_pooled_redis(db=0, conn=64):
        return redis.Redis(db=db, connection_pool=redis.ConnectionPool(max_connections=conn))

    def set(self, key, value, timeout=None):
        """
        Atomic cpickle & save & expired for python objects

        r.set('100500:over9000', {'lock': 0, 'mock':[1,2,3]})
        r.set('100500:42', set([10, 20, 30, 10, 40, 20]))
        r.set('100500:+100500', 'Russian cursive makes me cry sometimes', timeout=60 * 5)
        """
        timeout = timeout or self._timeout
        key = self._prefix + key
        self._redis.pipeline().set(key, pickle.dumps(value)).expire(key, timeout).execute()

    def get(self, key):
        """
        Get & unpickle python object by full specified key (if in db)
        
        r.get('100500:42') -> set([40, 10, 20, 30])
        """
        data = self._redis.get(self._prefix + key)
        return (data and pickle.loads(data)) or None

    def count(self, pattern=''):
        """
        Count number of existing values by mask
        
        r.count('100500:') -> 3        
        r.count() -> len of all values in db, for which key prefixed 
        """
        return len(self._redis.keys(self._prefix + pattern + '*'))

    def flush(self, pattern='', step=1000):
        """
        Chunked truncate db, remove matching keys
        
        r.flush('100500')
        """
        keys = self._redis.keys(self._prefix + pattern + '*')
        [self._redis.delete(*keys[i:i + step]) for i in xrange(0, len(keys), step)]

    def getall(self, pattern=''):
        """
        Get list of tuples (key, value)
        
        r.getall()
        r.getall('100500:')
        """
        # return self._redis.hvals(self._prefix + pattern)
        keys = self._redis.keys(self._prefix + pattern + '*')
        if keys:
            values = map(lambda data: (data and pickle.loads(data)) or None, self._redis.mget(keys))
            return zip(keys, values)
        return None

    def getall_as_iter(self, pattern=''):
        """
        Get iterator for matching objects: (key, value)
        
        r.getall_as_iter()        
        
        list( r.getall_as_iter() )
        
        for x in r.getall_as_iter('100500:'):
            x...        
        """
        keys = self._redis.keys(self._prefix + pattern + '*')
        values = imap(lambda data: (data and pickle.loads(data)) or None, self._redis.mget(keys))

        return izip(keys, values)

    def getall_as_dict(self, pattern=''):
        """
        Mapping view for matching objects { key: value, key: value, ...}

        """
        keys = self._redis.keys(self._prefix + pattern + '*')
        values = imap(lambda data: (data and pickle.loads(data)) or None, self._redis.mget(keys))

        return dict(izip(keys, values))

    @staticmethod
    def examples():

        r = RedCache(redis.Redis(db=9), '', 60 * 10)

        r.set('100500:over9000', {'lock': 0, 'mock': [1, 2, 3]})
        r.set('100500:42', set([10, 20, 30, 10, 40, 20]))
        r.set('100500:+100500', 'Russian cursive makes me cry sometimes', timeout=60 * 5)

        print r.get('100500:42')

        print r.getall()
        print r.getall('100500:')

        print r.count('100500:')
        print r.count()

        r.set('abc:123', (1, 2, 3,))
        r.set('abc:de', ['d', 'e'])
        print r.getall('abc:')
        r.flush('abc:')

        print r.getall_as_iter()
        print list(r.getall_as_iter())
        for x in r.getall_as_iter('100500:'):
            print x

        print r.getall_as_dict()
        print r.getall_as_dict('100500')
        r.flush()




red_cache = partial(RedCache, redis=Redis(db=9), prefix='cache|')


# class RedAsync(RedCache):
#     def __init__(self, prefix='kwpick|', timeout=60*1):
#         self._connection_pool = tornadoredis.ConnectionPool(max_connections=64, wait_for_available=True)
#         self._redis = tornadoredis.Client(selected_db=0, connection_pool=self._connection_pool)
#         self._prefix = prefix
#         self._timeout = timeout
#
#     @tornado.gen.engine
#     def set(self, key, value, timeout=None):
#         timeout = timeout or self._timeout
#         key = self._prefix + key
#
#         with self._redis.pipeline() as pipe:
#             pipe.set(key, pickle.dumps(value),timeout)
#             yield tornado.gen.Task(pipe.execute)


class PlanCache(redis.Redis):

    """ aka PlanCache(104).get_total() """
    # TO DO use global settings for redis

    def __init__(self, plan_id, host="localhost", port=_port, db=0, password="", *args, **kwargs):
        self.plan_id = plan_id
        self.custom_key = "plan:%s:custom" % self.plan_id
        self.auto_key = "plan:%s:auto" % self.plan_id
        self.info_key = "plan:%s:info" % self.plan_id
        self.grouping_key = "plan:%s:grouping" % self.plan_id
        super(PlanCache, self).__init__()  # *args, **kwargs

        self.expire(self.custom_key, 28800)
        self.expire(self.auto_key, 28800)
        self.expire(self.grouping_key, 28800)

    # TO DO decorator for response False if expired

    def reset_cache(self):
        self.delete(self.custom_key, self.auto_key, self.info_key, self.grouping_key)

    def push_init_data(self, data):
        self.lpush(self.custom_key, data)

    def pop_init_data(self):
        return self.lpop(self.custom_key)

    def push_grouping_data(self, data):
        self.lpush(self.grouping_key, data)

    def pop_grouping_data(self):
        return self.lpop(self.grouping_key)

    # not using yet
    def save_custom_query(self, query_id, wordstat, direct, wo_forms, phrase):
        """ PlanCache(104).save_custom_query(....) """
        self.hset(self.custom_key, query_id, [
            query_id, wordstat, direct, wo_forms, phrase
        ])

    def get_custom_length(self):
        return self.hlen(self.custom_key) * 3

    def get_custom_pending(self):
        try:
            result = (eval(x)[1:4] for x in self.hvals(self.custom_key))
            return reduce(operator.add, result).count(None)
        except TypeError:
            return 0

    def get_custom_doned(self):
        return self.get_custom_length() - self.get_custom_pending()

    def get_custom_balance(self):
        return (self.get_custom_doned(), self.get_custom_length())

    def save_auto_query(self, query_id, wordstat, direct, wo_forms, phrase):
        self.hset(self.auto_key, query_id, [
            query_id, wordstat, direct, wo_forms, phrase
        ])

    def get_auto_length(self):
        return self.hlen(self.auto_key)

    def get_auto_pending(self):
        try:
            result = (eval(x)[1:4] for x in self.hvals(self.auto_key))
            return reduce(operator.add, result).count(None)
        except TypeError:
            return 0

    def get_auto_doned(self):
        return self.get_auto_length() - self.get_auto_pending()

    def get_auto_balance(self):
        return (self.get_auto_doned(), self.get_auto_length())

    def get_common_balance(self):
        return map(sum, zip(self.get_custom_balance(), self.get_auto_balance()))

    def get_total(self):
        return (self.get_auto_length() + self.get_custom_length()) * 3
