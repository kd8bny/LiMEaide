#!/bin/python

import sys
import os
import json
import getpass
import datetime

from client import Client


class Profiler(object):
    """Maintain and impliment built profiles. Call main to init the profiles."""

    def __init__(self):
        super(Profiler, self).__init__()
        self.profiles = []
        self.profiles_dir = './profiles/'
        self.manifest = 'manifest.json'

    def load_profiles(self):
        try:
            self.profiles = json.load(
                open(self.profiles_dir + self.manifest, 'r').close())
        except FileNotFoundError as e:
            pass

    def save_profile(self, distro, kver, arch):
        if profile is None:
            profile = {
                "distro": distro,
                "kver": kver,
                "arch": arch,
                "module": "lime-{0}-{1}.ko".format(distro, kver),
                "profile": "vol-{0}-{1}.zip".format(distro, kver)
                }
            self.profiles.append(profile)
        json.dump(self.profiles, open(self.profiles_dir + self.manifest, 'w'))

        return profile

    def interactive_chooser(self):
        """Interactive CLI mode for choosing pre-compiled modules. The profiles
        are a list of dicts."""
        profile_dict = None
        if len(self.profiles) > 0:
            while True:
                for i, profile in enumerate(self.profiles):
                    print(
                        "%i) %s, %s, %s\t" %
                        (i, profile['distro'], profile['kver'], profile['arch']))
                profile_val = input(
                    "Please select a profile. Press [q] to exit: ")
                if profile_val > 1 or profile_val < len(self.profiles):
                    return profile

                else:
                    if distro_val == 'q':
                        return None
                    else:
                        print("Please select a correct value and try agin")

    def select_profile(self, distro, kver, arch):
        """Select a profile to have the client use."""
        if len(self.profiles) > 0:
            for i, profile in enumerate(self.profiles):
                if profile['distro'] is distro and profile['kver'] is kver and profile['arch'] is arch:
                    return profile

                else:
                    return None

    def main(self):
        self.load_profiles()
