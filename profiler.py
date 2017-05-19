#!/bin/python

import sys
import os
import json
import getpass
import datetime

from client import Client


class Profiler(object):
    """Maintain and impliment built profiles"""

    def __init__(self):
        super(Profiler, self).__init__()
        self.profiles = []
        self.profiles_dir = './profiles/'
        self.manifest = 'manifest.json'

    def save_profile(self, distro, kver, arch):
        if profile is None:
            profile = {
                "distro": distro,
                "kver": kver,
                "arch": arch,
                "module": "lime-{0}-{1}.ko".format(distro, kver)
                "profile": "vol-{0}-{1}.zip".format(distro, kver)
                }
            self.profiles.append(profile)
        json.dump(self.profiles, file.write(self.profiles_dir + self.manifest))

        return profile

    def load_profiles(self):
        try:
            self.profiles = json.load(
                file.read(self.profiles_dir + self.manifest))
        except FileNotFoundError as e:
            pass

    def interactive_chooser(self):
        selected_distro, selected_kver = None
        if len(self.profiles) > 0:
            distro_list = list(self.profiles)
            while True:
                for i, distro in enumerate(distro_list):
                    print("%i) %s\t" % (i, distro))
                distro_val = input("Please select a distribution")
                if distro_val > 1 or distro_val < len(self.profiles):
                    kver_list = self.profiles[distro_list[distro_val]]
                    for i, kver in enumerate(kver_list):
                        print("%i) %s\t" % (i, distro))
                else:
                    if distro_val == 'q':
                        sys.exit()
                    else:
                        print("Please select a correct value and try agin")
                    kver_val = input("Please select a kernel version")
                    if kver_val > 1 or kver_val < len(kver_list):
                        break
                    else:
                        if distro_val == 'q':
                            sys.exit()
                        else:
                            print("Please select a correct value and try agin")

        return selected_distro, selected_kver

    def main(self):
        self.populate_profiles()


if __name__ == '__main__':
    Profiler().main()
