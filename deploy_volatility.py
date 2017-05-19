#!/bin/python

import sys
import os
from subprocess import Popen, PIPE
from client import Client


class VolDeploy(object):
    """Develops Volatility profile to analyze dump"""
    def __init__(self, session):
        super(VolDeploy, self).__init__()
        self.client = session.client_
        self.remote_session = session
        self.lime_rdir = '/tmp/lime/'
        self.map = 'System.map-%s' % self.client.kver

    def get_maps(self):
        print("Obtaining System.maps")
        self.remote_session.exec_cmd(
            "cp /boot/%s %s" % (self.map, self.lime_rdir), True)
        self.remote_session.exec_cmd(
            "chmod 744 %s%s" % (self.lime_rdir, self.map), True)
        error = self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, self.map)

        if error:
            sys.exit("Map not found cannot build profile")

        print("done.")

    def get_profile(self):
        print("Obtaining symbols")
        dwarf_file = open(
            self.client.output_dir + self.client.kver + '.dwarf', 'w+')
        sp = Popen(
            ['dwarfdump', '-d', '-i', self.client.output_dir + self.client.module],
             stdout=dwarf_file)
        sp.wait()
        dwarf_file.flush()

        Popen(['zip', '-j', self.client.output_dir + self.client.kver + '.zip',
                self.client.output_dir + self.client.kver + '.dwarf', self.client.output_dir + self.map])
        print("done.")

    def main(self):
        print("Attempting to grab files for volatility profile")
        self.get_maps()
        self.get_profile()
        print("Profile complete place in volatility/plugins/overlays/linux/ in\
            order to use")


if __name__ == '__main__':
    VolDeploy().main()
