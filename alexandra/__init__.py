import pycassa
from django.conf import settings

__version__ = (0,1)

client = pycassa.connect_thread_local(settings.CASSANDRA_CLUSTER)
