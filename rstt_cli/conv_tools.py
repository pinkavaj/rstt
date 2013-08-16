
from struct import unpack


_int_min = -0x1400000
_int_max = (0x1400000-1)

def conv_int(data):
    """Convert 3/4 bytes in fract24 format into int."""
    if len(data) == 3:
        data = data + b'\x00'
    val = unpack('<i', data)[0]
    if val > _int_max or val < _int_min:
        return None
    return val


def conv_fract(data):
    """Convert 3 or 4 byte in fract24 format to float."""
    val = conv_int(data)
    if val is None:
        return float('NAN')
    return float(val)

