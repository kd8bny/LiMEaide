#!/bin/python

import sys, datetime, os, argparse, getpass
from session import Session
from client import Client


class Limeaide(object):
    """processes all interactions with remote client"""
    def __init__(self):
        super(Limeaide, self).__init__()
        self.lime_dir = './tools/LiME/src/'
        self.lime_rdir = './lime/'
        self.output_dir = './output/'
        self.lime = ['disk.c', 'lime.h', 'main.c', 'Makefile', 'tcp.c']
        self.remote_session = None

    def send_lime(self):
        print("sending LiME")
        self.remote_session.exec_cmd('mkdir %s' %self.lime_rdir, False)
        for file in self.lime:
            self.remote_session.put_sftp(self.lime_dir, self.lime_rdir, file)
        print("done.")

    def build_lime(self, client):
        print("building kernel module")
        self.remote_session.exec_cmd('cd %s; make' %self.lime_rdir, False)
        self.remote_session.exec_cmd('mv %s/lime*.ko .' %self.lime_rdir, False)
        self.remote_session.exec_cmd('insmod lime*.ko "path=%s format=raw dio=0"' %client.output, True)
        print("done.")

    def get_lime(self, client):
        print("Changing permissions")
        self.remote_session.exec_cmd('chmod 755 %s' %client.output, True)
        print("Beam me up Scotty")
        self.remote_session.pull_sftp(".", self.output_dir, client.output)

    def clean(self, client):
        print("cleaning up...")
        self.remote_session.exec_cmd('rm -r lime* %s' %client.output, True)
        print("Removing LKM...standby")
        self.remote_session.exec_cmd('rmmod lime.ko', True)
        print("Memory extraction is complete")

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
        client.pass_ = getpass.getpass()

        self.remote_session = Session(client)
        self.send_lime()
        self.build_lime(client)
        self.get_lime(client)
        self.clean(client)

if __name__ == '__main__':
    Limeaide().main()
