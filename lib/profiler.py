# LiMEaide
# Copyright (c) 2011-2018 Daryl Bennett

# Author:
# Daryl Bennett - kd8bny@gmail.com

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os
import logging
import re
import fnmatch
import json
import shutil
from termcolor import colored, cprint


class Profiler(object):
    """Maintain and implement pre-compiled modules and profiles."""

    def __init__(self, config):
        super(Profiler, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.profiles_dir = config.profile_dir
        self.manifest = config.manifest

        self.profiles = []

    def __clean_manifest__(self):
        """Determine if profile need to be cleaned.

        Returns bool notifying the need to reload profiles.
        """

        disk_modules = fnmatch.filter(
            os.listdir(self.profiles_dir), '*.ko')

        if len(disk_modules) != len(self.profiles):
            cprint("> Cleaning profile manifest", 'blue')
            self.logger.info("Cleaning profile manifest")

            existing_profiles = []
            for profile in self.profiles:
                if profile['module'] not in disk_modules:
                    self.logger.info(
                        "Profile {0} {1} {2} not found. Removing".format(
                            profile["distro"], profile["kver"],
                            profile["arch"]))

                    continue

                self.logger.info(
                    "Profile {0} {1} {2} exists".format(
                        profile["distro"], profile["kver"],
                        profile["arch"]))

                disk_modules.pop(disk_modules.index(profile['module']))
                existing_profiles.append(profile)

            if len(disk_modules) > 0:
                cprint("> Importing new modules", 'green')

                for module in disk_modules:
                    self.logger.info(
                        "Profile {} found. Importing".format(module))
                    cprint("> Module {}".format(module), 'yellow')
                    distro = input(colored(
                        "Distribution: ", 'green')).lower().replace(' ', '')
                    kver = input(colored(
                        "Kernel Version: ", 'green')).lower().replace(' ', '')
                    arch = input(colored(
                        "Architecture: ", 'green')).lower().replace(' ', '')

                    profile = {
                        "distro": distro,
                        "kver": kver,
                        "arch": arch,
                        "module": "lime-{0}-{1}-{2}.ko".format(
                            distro, kver, arch),
                        "profile": "vol-{0}-{1}-{2}.zip".format(
                            distro, kver, arch)}

                    shutil.move(
                        self.profiles_dir + module,
                        self.profiles_dir + profile['module'])

                    existing_profiles.append(profile)

            self.profiles = existing_profiles
            json.dump(
                self.profiles, open(self.profiles_dir + self.manifest, 'w'))

            return True

        return False

    def load_profiles(self):
        """Load dict from JSON manifest."""
        try:
            self.profiles = json.load(
                open(self.profiles_dir + self.manifest, 'r'))
        except FileNotFoundError as e:
            self.logger.info(str(e) + "This could be a first run")

        reload_profiles = self.__clean_manifest__()
        if reload_profiles:
            self.load_profiles()

    def create_profile(self, remote_session):
        """Create a new profile a save to manifest.

        Look through the output of uname and lsb_release to determine
        versions.
        """
        distro, kver, arch = '', '', ''
        releases = remote_session.exec_cmd("cd /etc/; ls *-release")

        if len(releases) > 0:
            if 'os-release' in releases:
                os_release = remote_session.exec_cmd(
                    "cat /etc/{}".format('os-release'))

                distro = list(filter(lambda val: val.startswith(
                    'PRETTY_NAME='), os_release))
                distro = distro[0].split('=')
                distro = distro[1]

            elif 'lsb-release' in releases:
                lsb_release = remote_session.exec_cmd(
                    "cat /etc/{}".format('lsb-release'))

                distro = list(filter(lambda val: val.startswith(
                    'DISTRIB_DESCRIPTION='), lsb_release))
                distro = distro[0].split('=')
                distro = distro[1]

            else:
                os_release = remote_session.exec_cmd(
                    "cat /etc/{}".format(releases[0]))

            distro = re.sub('[^a-zA-Z0-9-\s_*.]', '', distro)
            distro = re.sub('\s', '-', distro)
            distro = distro.lower()

        if not distro:
            distro = input(colored("Cannot determine distribution. Please " +
                                   "enter distribution name: ", 'red'))

        uname = remote_session.exec_cmd('uname -rm')
        kver = uname[0]
        arch = uname[1]

        profile = {
            "distro": distro,
            "kver": kver,
            "arch": arch,
            "module": "lime-{0}-{1}-{2}.ko".format(distro, kver, arch),
            "profile": "vol-{0}-{1}-{2}.zip".format(distro, kver, arch)}

        self.profiles.append(profile)
        json.dump(self.profiles, open(self.profiles_dir + self.manifest, 'w'))

        return profile

    def interactive_chooser(self):
        """Interactive CLI mode for choosing pre-compiled modules.

        :return None to exit, otherwise it returns a json profile
        """
        num_profiles = len(self.profiles)
        if num_profiles > 0:
            while True:
                for i, profile in enumerate(self.profiles):
                    print(
                        "%i) %s, %s, %s\t" %
                        (i, profile['distro'], profile['kver'],
                         profile['arch']))

                profile_val = int(input(
                    "Please select a profile. " +
                    "Enter [{}] to exit: ".format(num_profiles)))

                if profile_val == num_profiles:
                    return None
                elif profile_val > 1 or profile_val < num_profiles:
                    return self.profiles[profile_val]
                else:
                    print("Please select a correct value and try agin")

    def select_profile(self, distro, kver, arch):
        """Select a profile to have the client use."""
        num_profiles = len(self.profiles)
        if num_profiles > 0:
            for profile in self.profiles:
                if profile['distro'] == distro:
                    if profile['kver'] == kver:
                        if profile['arch'] == arch:
                            return profile

        return None
