import struct

def _long(i):
    """
    Packs a long into the expected sequence of bytes that Cassandra expects.
    """
    return struct.pack('>d', long(i))
 
def _unlong(b):
    """
    Unpacks Cassandra's byte-representation of longs into their Python long
    equivalents.
    """
    return struct.unpack('>d', b)[0]
    