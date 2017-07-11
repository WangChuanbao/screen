# -*- coding: UTF-8 -*-
# author: star
# created_at: 17-6-29 10:26
import threading
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR

from core import settings
from core.consumers import pizza_done


def udpReceiveDataFor():
    HOST = settings.UDP.get('HOST') or ''
    PORT = settings.UDP.get('PORT') or 7788

    BUF_SIZE = settings.UDP.get('BUF_SIZE') or 1024

    sk = socket(AF_INET, SOCK_DGRAM)
    sk.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sk.bind((HOST, PORT))

    while True:
        data, addr = sk.recvfrom(BUF_SIZE)
        pizza_done.send(sender=addr, toppings=data, size=BUF_SIZE)

t = threading.Thread(target=udpReceiveDataFor)
t.start()
