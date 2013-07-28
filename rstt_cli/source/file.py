
class File:
    def __init__(self, file_name):
        self._f = open(file_name, 'rb')

    def get_frame(self):
        return self._f.read(2*240)
