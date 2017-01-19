#!/bin/python

import sys, datetime, os, argparse
from session import Session
from client import Client


class Limeaide(object):
    """processes all interactions with remote client"""
    def __init__(self):
        super(Limeaide, self).__init__()
        self.lime_dir = './tools/LiME/src/'
        self.lime = ['disk.c', 'lime.h', 'main.c', 'Makefile', 'tcp.c']
        self.remote_session = None

    def send_lime(self):
        print("sending LiME")
        self.remote_session.exec_cmd('mkdir lime', False)
        self.remote_session.exec_cmd('cd lime/', False)
        for file in self.lime:
            self.remote_session.put_sftp(self.lime_dir, file)
        print("done.")

    def build_lime(self, client):
        print("building kernel module")
        self.remote_session.exec_cmd('make', False)
        self.remote_session.exec_cmd('insmod ./lime/lime.ko "path=%s format=raw dio=0"' %client.output, True)
        print("done.")

    def get_lime(self):
        print("Beam me up Scotty")
        self.remote_session.pull_sftp(self.lime_dir, file)

    def clean(self):
        print("cleaning up...")
        self.remote_session.exec_cmd('cd .. && rm -r lime/', True)
        self.remote_session.close()
        print("done.")

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("remote", help="remote host IP")
        
        parser.add_argument("-s", "--sudoer", help="use a sudo user instead default: root")
        parser.add_argument("-o", "--output", help="name the outputfile")
        args = parser.parse_args()
        
        client = Client()
        client.ip = args.remote
        if args.sudoer != None:
            client.user = args.sudoer
            client.is_sudoer = True
        if args.output != None:
            client.output = args.output
        
        print("Attempting secure connection %s@%s" %(client.user, client.ip))
        print("Password for %s:" %client.user)
        client.pass_ = raw_input()

        self.remote_session = Session(client)
        self.send_lime()
        self.build_lime(client)
        #self.clean()        

if __name__ == '__main__':
    Limeaide().main()
