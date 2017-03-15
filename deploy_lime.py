#!/bin/python

import sys, datetime, os
from client import Client


class LimeDeploy(object):
    """processes all interactions with remote client"""
    def __init__(self, session):
        super(LimeDeploy, self).__init__()
        self.client = session.client_
        self.remote_session = session
        self.lime_dir = './tools/LiME/src/'
        self.lime_rdir = './lime/'
        self.lime_src = ['disk.c', 'lime.h', 'main.c', 'Makefile']

    def send_lime(self):
        print("sending LiME")
        self.remote_session.exec_cmd('mkdir %s' %self.lime_rdir, False)
        for file in self.lime_src:
            self.remote_session.put_sftp(self.lime_dir, self.lime_rdir, file)
        print("done.")

    def build_lime(self):
        stdout = self.remote_session.exec_cmd('uname -r', False)
        self.client.kver = stdout[0].strip()
        self.client.module = 'lime-%s.ko' %self.client.kver
        print("building kernel module %s" %self.client.kver)
        self.remote_session.exec_cmd('cd %s; make' %self.lime_rdir, False)
        self.remote_session.exec_cmd('mv %s/%s .' %(self.lime_rdir, self.client.module), False)
        print("Installing LKM and retrieving RAM")
        self.remote_session.exec_cmd('insmod %s "path=%s format=lime dio=0"' %(self.client.module, self.client.output), True) #TODO test on centOS
        print("done.")

    def get_lime(self):
        print("Changing permissions")
        self.remote_session.exec_cmd('chmod 755 %s' %self.client.output, True)

        if self.client.compress:
            print("Creating Bzip2...compressing the following")
            self.remote_session.exec_cmd('tar -jv --remove-files -f %s.bz2 -c %s'
                    %(self.client.output, self.client.output), True)
            self.client.output += ".bz2"

        print("Beam me up Scotty")
        self.remote_session.pull_sftp(".", self.client.output_dir, self.client.output)
        self.remote_session.pull_sftp(".", self.client.output_dir, self.client.module)

    def main(self):
        self.send_lime()
        self.build_lime()
        self.get_lime()

if __name__ == '__main__':
    LimeDeploy().main()
