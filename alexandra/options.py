from django.db.models.options import get_verbose_name
from django.conf import settings

from alexandra.exceptions import ConfigurationError
from alexandra.manager import Manager

DEFAULT_NAMES = ('verbose_name', 'app_label', 'keyspace', 'super_cf', 'read_consistency_level', 'write_consistency_level')

class Options(object):
    
    def __init__(self, meta, app_label=None):
        
        self.meta = meta
        self.app_label = app_label
        self.object_name = None
        self.verbose_name = None
        self.keyspace = getattr(settings,'CASSANDRA_KEYSPACE','')
        self.super_cf = False
        self.pk = None
        self.read_consistency_level = None
        self.write_consistency_level = None
    
    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.object_name = cls.__name__
        self.verbose_name = get_verbose_name(self.object_name)
        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))
        
        if not self.keyspace:
            raise ConfigurationError(u"No keyspace defined! Define keyspace in your model's Meta class or CASSANDRA_KEYSPACE in settings.py")
        
        if getattr(settings, 'RUNNING_TESTS', False):
            self.keyspace = 'test_%s' % self.keyspace
        cls.add_to_class('objects', Manager())        

        del self.meta
    