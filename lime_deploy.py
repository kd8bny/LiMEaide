#!/bin/python

import sys, datetime, os
from session import Session
from client import Client


class LimeDeploy(object):
    """processes all interactions with remote client"""
    def __init__(self, client):
        super(LimeDeploy, self).__init__()
        self.client = client
        self.remote_session = Session(self.client)
        self.lime_dir = './tools/LiME/src/'
        self.lime_rdir = './lime/'
        self.output_dir = './output/'
        self.lime = ['disk.c', 'lime.h', 'main.c', 'Makefile', 'tcp.c']

    def send_lime(self):
        print("sending LiME")
        self.remote_session.exec_cmd('mkdir %s' %self.lime_rdir, False)
        for file in self.lime:
            self.remote_session.put_sftp(self.lime_dir, self.lime_rdir, file)
        print("done.")

    def build_lime(self):
        print("building kernel module")
        self.remote_session.exec_cmd('cd %s; make' %self.lime_rdir, False)
        self.remote_session.exec_cmd('mv %s/lime*.ko .' %self.lime_rdir, False)
        print("Installing LKM and retrieving RAM")
        self.remote_session.exec_cmd('insmod lime*.ko "path=%s format=raw dio=0"' %self.client.output, True) #TODO test on centOS
        print("done.")

    def get_lime(self):
        print("Changing permissions")
        self.remote_session.exec_cmd('chmod 755 %s' %self.client.output, True)
        if self.client.dont_compress:
            print("Beam me up Scotty")
            self.remote_session.pull_sftp(".", self.output_dir, self.client.output)
        else:
            print("Creating Bzip2")
            self.remote_session.exec_cmd('tar -jv --remove-files -f %s.bz2 -c %s'
                    %(self.client.output, self.client.output), False)
            print("Beam me up Scotty")
            self.remote_session.pull_sftp(".", self.output_dir, self.client.output + ".bz2")

    def clean(self):
        print("cleaning up...")
        self.remote_session.exec_cmd('rm -r lime* %s*' %self.client.output, True)
        print("Removing LKM...standby")
        self.remote_session.exec_cmd('rmmod lime.ko', True)

    def main(self):
        self.send_lime()
        self.build_lime()
        self.get_lime()
        self.clean()
        print("Memory extraction is complete\n\n%s is in %s" %(self.client.output, self.output_dir))

if __name__ == '__main__':
    LimeDeploy().main()
