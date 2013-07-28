
from source.file import File
from source.udp import Udp


def open(url):
    url = url.split(':', 1)
    if len(url) == 1:
        return File(url[0])
    proto, src = url
    if proto == 'file://':
        return File(src)
    if proto == 'udp://':
        return Udp(src)
    raise ValueError("Unsupported protocol or URL format")

