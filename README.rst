alexandra
=========

alexandra is a thin abstraction over pycassa to interact with Cassandra from Django.

Installation
************

Requires Django and `pycassa 0.20`_ or greater::

    pip install -e git+git@github.com:dziegler/alexandra.git#egg=alexandra  

.. _`pycassa 0.20`: http://github.com/vomjom/pycassa


Sample Usage
************
Syntax for model definition is similar to Django's, but because rows can have as many columns as you want, there's no need to define them.::

    import pycassa
    from alexandra import cass

    class EventManager(cass.Manager):
    
        def get_for_uuid(self, uuid):
            return self.get(uuid)

    class Event(cass.ColumnFamily):
        """
        Event = {
            "89c23f26377e439a8e52fadec8f6bf19" = {
                "uuid": "804e39e29a6148039633e5a69f0c0870",
                "action": "landing:home"
                "ip_address": "127.0.0.1",
                "gender": "1",
            }
            ...
        }
        """
        objects = EventManager()
    
        class Meta:
            write_consistency_level = pycassa.ConsistencyLevel.QUORUM
    
        def save(self, *args, **kwargs):
            super(Event, self).save(*args, **kwargs)
            TrackingUUID.objects.add_event(self['uuid'], self.pk)
        

Queries use the pycassa query api, along with whatever other methods you want to define in your manager::

        Event.objects.multiget([1, 2])
        Event.objects.get_for_uuid(['asdf93'])
        
