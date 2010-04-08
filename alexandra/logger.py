import threading
import pycassa
from time import time

from alexandra import client

class CassandraLogger(threading.local):

    def __init__(self, client):
        self.client = client
        self.reset()

    def reset(self):
        self.log = []
    
    def delete_log_contents(self):
        for log in self.log:
            if log.name == 'insert':
                cp = pycassa.columnfamily.ColumnPath(column_family=log.column_family)
                self.client.remove(log.keyspace, log.keys, cp, pycassa.gm_timestamp(), pycassa.ConsistencyLevel.ALL)

cass_logger = CassandraLogger(client)


class CassandraLogInstance(object):

    def __init__(self, name, keyspace=None, column_family=None, keys=None, columns=None, func_time=None):
        self.name = name
        self.keyspace = keyspace
        self.column_family = column_family
        self.keys = keys
        self.columns = columns
        self.time = func_time
    
    def __repr__(self):
        return u' - '.join((self.name, unicode(self.column_family), unicode(self.keys), unicode(self.columns)))


def logged_func(func):
    if getattr(func, '_decorated', False):
        return func
        
    def inner(instance, *args, **kwargs):
        start = time()
        val = func(instance, *args, **kwargs)
        func_time = time() - start
        
        if func.func_name in ('get', 'multiget', 'get_count', 'insert', 'remove'):
            log_args = dict(zip(('keys', 'columns'), args))
            for key in ('key', 'keys'):
                if key in kwargs:
                    log_args['keys'] = kwargs[key]
            for key in ('column', 'columns','super_column'):
                if key in kwargs:
                    log_args['columns'] = kwargs[key]
            log_args['keyspace'] = instance.keyspace
            log_args['column_family'] = instance.column_family
            log_args['func_time'] = func_time
            cass_logger.log.append(CassandraLogInstance(func.func_name, **log_args))
        return val
    inner._decorated = True
    return inner