import pycassa
import inspect
from django.conf import settings
from django.db.models.manager import ManagerDescriptor

from alexandra import client

class MetaManager(type):
    def __init__(cls, name, bases, attrs):
        if settings.DEBUG:
            from alexandra.logger import logged_func

            for base in bases:
                for attr in dir(base):
                    value = getattr(base, attr)
                    if not attr.startswith('_') and inspect.ismethod(value):
                        setattr(cls, attr, logged_func(value))
            
            for attr, value in attrs.items():
                if not attr.startswith('_') and inspect.isfunction(value):
                    setattr(cls, attr, logged_func(value))
 

class Manager(pycassa.ColumnFamily):
    
    __metaclass__ = MetaManager
    
    def __init__(self):
        self.model = None
    
    def contribute_to_class(self, model, name,):
        self.model = model
        setattr(model, name, ManagerDescriptor(self))
        meta = model._meta
        super(Manager, self).__init__(client, meta.keyspace, meta.object_name, dict_class=model, super=meta.super_cf)
        if meta.write_consistency_level is not None:
            self.write_consistency_level = meta.write_consistency_level
        if meta.read_consistency_level is not None:
            self.read_consistency_level = meta.read_consistency_level
    
    def get(self, key, **kwargs):
        if 'column_count' not in kwargs:
            kwargs['column_count'] = 1000000
        obj = super(Manager, self).get(key, **kwargs)
        obj.pk = key
        return obj
    
    def multiget(self, keys, **kwargs):
        if 'column_count' not in kwargs:
            kwargs['column_count'] = 1000000
        objs = super(Manager, self).multiget(keys, **kwargs)
        for k, v in objs.iteritems():
            v.pk = k
        return objs
    
    def insert(self, key, columns, write_consistency_level=None):
        obj = self.model(**columns)
        obj.pk = key
        return obj.save(write_consistency_level=write_consistency_level)
    
    def _insert(self, key, columns, write_consistency_level=None):
        for k,v in columns.iteritems():
            if isinstance(v, dict):
                for subk, subv in v.iteritems():
                    columns[k][subk] = unicode(subv)
            else:
                columns[k] = unicode(v)
        return super(Manager, self).insert(key, columns, write_consistency_level=write_consistency_level)
        
    def _remove(self, key, column=None, write_consistency_level = None):
        return super(Manager, self).remove(key, column=column, write_consistency_level=write_consistency_level)
    
