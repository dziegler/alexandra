import sys
import pycassa
from odict import OrderedDict
from django.db.models.base import subclass_exception

from alexandra.options import Options
from alexandra.exceptions import AlexandraException
from alexandra.manager import Manager

class ColumnFamilyBase(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(ColumnFamilyBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ColumnFamilyBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        # Create the class
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        meta = attrs.pop('Meta', None)
        if not meta:
            meta = getattr(new_class, 'Meta', None)
        base_meta = getattr(new_class, '_meta', None)
        
        if getattr(meta, 'app_label', None) is None:
            # Figure out the app_label by looking one level up.
            # For 'django.contrib.sites.models', this would be 'sites'.
            model_module = sys.modules[new_class.__module__]
            kwargs = {"app_label": model_module.__name__.split('.')[-2]}
        else:
            kwargs = {}
        
        new_class.add_to_class('_meta', Options(meta, **kwargs))
        new_class.add_to_class('NotFoundException', pycassa.NotFoundException)
        
        # Add all attributes to the class.
        for obj_name, obj in attrs.iteritems():
            new_class.add_to_class(obj_name, obj)
        return new_class       
        
    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)
    

class ColumnFamily(OrderedDict):
    __metaclass__ = ColumnFamilyBase
    
    def __init__(self, *args, **kwargs):
        super(ColumnFamily, self).__init__(*args, **kwargs)
        self.pk = None
    
    def save(self, write_consistency_level=None):
        return self.__class__.objects._insert(self.pk, self, write_consistency_level=write_consistency_level)
    
    def delete(self, column=None, write_consistency_level=None):
        return self.__class__.objects._remove(self.pk, column=column, write_consistency_level=write_consistency_level)
        
        
    