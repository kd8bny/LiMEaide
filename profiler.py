#!/bin/python

import sys, os, argparse, getpass
from datetime import datetime
from client import Client


class Profiler(object):
    """Maintain and impliment built profiles"""

    def __init__(self):
        super(Profiler, self).__init__()
        self.profiles = [] #dict of lists to retain profiles
        self.profiles_dir = './profiles/'

    def new_profile(self, distro, kver, profile, lkm):
        distro_path = self.profiles_dir + distro
        kver_path = distro_path + '/' + kver
        if not os.path.isdir(distro_path):
            os.mkdir(distro_path)

        if not os.path.isdir(kver_path):
            os.mkdir(kver_path)

        #Copy profiles

    def gen_profiles(self):
        #in the future pickle to save time
        for #ea distor dir in profiles:
            distro []
            for # ea kver:
                distro.add(kver)
            self.profiles.add(distro)

    def list_profiles(self):
        for distro in dict.keys(self.profiles):
            print("Distro: %s", distro)
            for kver in self.profiles[distro]:
                print("kernel: %s", kver)

    def main(self):
        self.gen_profiles()

if __name__ == '__main__':
    Profiler().main()
