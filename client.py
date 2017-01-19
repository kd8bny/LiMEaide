#!/bin/python

class Client(object):
    """Define client connection"""
    def __init__(self):
        super(Client, self).__init__
        self.user = 'root'
        self.pass_ = None
        self.ip = None
        self.output = 'dump.bin'
        self.is_sudoer = False
