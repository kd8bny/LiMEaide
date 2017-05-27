#!/bin/python

import sys
import os
import datetime

from client import Client
from profiler import Profiler


class LimeDeploy(object):
    """processes all interactions with remote client"""
    def __init__(self, session, profiler):
        super(LimeDeploy, self).__init__()
        self.remote_session = session
        self.client = session.client_
        self.profiler = profiler
        self.lime_dir = './tools/LiME/src/'
        self.lime_rdir = '/tmp/lime/'
        self.lime_src = ['disk.c', 'lime.h', 'main.c', 'Makefile']
        self.profiles_dir = './profiles/'

    def send_lime(self):
        print("sending LiME to remote client")
        self.remote_session.exec_cmd('mkdir %s' % self.lime_rdir, False)
        if self.client.profile is None:
            for file in self.lime_src:
                self.remote_session.put_sftp(
                    self.lime_dir, self.lime_rdir, file)

            stdout = self.remote_session.exec_cmd('cat /etc/issue', False)
            distro = stdout[0].strip()
            stdout = self.remote_session.exec_cmd('uname -rm', False)
            print(stdout)
            kver = stdout[0].strip()
            arch = stdout[1].strip()
            self.client.profile = self.profiler.save_profile(distro, kver, arch)

            print("building kernel module {}".format(kver))
            self.remote_session.exec_cmd(
                'cd {}; make'.format(self.lime_rdir), False)
        else:
            self.remote_session.put_sftp(
                self.lime_dir, self.lime_rdir,
                self.profiles_dir + self.client.profile["module"])
        print("done.")

        return

    def get_lime_dump(self):
        print("Installing LKM and retrieving RAM")
        self.remote_session.exec_cmd(
            "insmod {0}{1} 'path={2}{3} format=lime dio=0'".format(
                self.lime_rdir, self.client.profile["module"], self.lime_rdir,
                self.client.output), True)
        print("done.")
        print("Changing permissions")
        self.remote_session.exec_cmd(
            "chmod 755 {0}{1}".format(
                self.lime_rdir, self.client.output), True)
        print("done.")
        if self.client.compress:
            print("Creating Bzip2...compressing the following")
            self.remote_session.exec_cmd(
                'tar -jv --remove-files -f {0}{1}.bz2 -c {2}{3}'.format(
                    self.lime_rdir, self.client.output, self.lime_rdir,
                    self.client.output), True)
            self.client.output += ".bz2"
            print("done.")

        print("Beam me up Scotty")
        self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, self.client.output)
        self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, self.client.module)

    def main(self):
        self.send_lime()
        self.get_lime()


if __name__ == '__main__':
    LimeDeploy().main()
