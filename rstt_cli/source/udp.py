#!/usr/bin/python3

import socket

class Udp:
    """UDP client for reversing data from meteosonde."""

    def __init__(self, address):
        host, port = address.split(':')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, int(port)))

    def get_frame(self):
      data, server = self.sock.recvfrom(1024)
      return data

