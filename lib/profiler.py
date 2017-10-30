import os
import re
import fnmatch
import contextlib
import json
from termcolor import colored, cprint


class Profiler(object):
    """Maintain and implement pre-compiled modules and profiles."""

    def __init__(self):
        super(Profiler, self).__init__()
        self.profiles = []
        self.profiles_dir = './profiles/'
        self.manifest = 'manifest.json'

    def __clean_manifest__(self):
        """Determine if profile need to be cleaned.

        Returns bool notifying the need to reload profiles.
        """
        num_profiles = len(fnmatch.filter(
            os.listdir(self.profiles_dir), 'lime-*.ko'))

        if num_profiles != len(self.profiles):
            cprint("> Cleaning profile manifest", 'blue')
            existing_profiles = []
            for profile in self.profiles:
                if profile in existing_profiles:
                    continue

                elif ((os.path.isfile(
                        self.profiles_dir + profile['module'])) and
                      (os.path.isfile(
                          self.profiles_dir + profile['profile']))):
                    existing_profiles.append(profile)
                else:
                    with contextlib.suppress(FileNotFoundError):
                        os.remove(self.profiles_dir + profile['module'])
                        os.remove(self.profiles_dir + profile['profile'])

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
            print(e)

        reload_profiles = self.__clean_manifest__()
        if reload_profiles:
            self.load_profiles()

    def create_profile(self, remote_session):
        """Create a new profile a save to manifest.

        Look through the output of uname and lsb_release to determine
        versions.
        """
        distro, kver, arch = '', '', ''
        releases = remote_session.exec_cmd("cd /etc/; ls *-release", False)
        releases = releases[0].split()

        if len(releases) > 0:
            if 'os-release' in releases:
                os_release = remote_session.exec_cmd(
                    "cat /etc/{}".format('os-release'), False)

                distro = list(filter(lambda val: val.startswith(
                    'PRETTY_NAME='), os_release))
                distro = distro[0].split('=')
                distro = distro[1]

            elif 'lsb-release' in releases:
                lsb_release = remote_session.exec_cmd(
                    "cat /etc/{}".format('lsb-release'), False)

                distro = list(filter(lambda val: val.startswith(
                    'DISTRIB_DESCRIPTION='), lsb_release))
                distro = distro[0].split('=')
                distro = distro[1]

            else:
                os_release = remote_session.exec_cmd(
                    "cat /etc/{}".format(releases[0]), False)

            distro = re.sub('[^a-zA-Z0-9-\s_*.]', '', distro)
            distro = re.sub('\s', '-', distro)
            distro = distro.lower()

        if not distro:
            distro = input(colored("Cannot determine distribution. Please " +
                                   "enter distribution name: ", 'red'))

        uname = remote_session.exec_cmd('uname -rm', False)
        kver, arch = uname[0].split()

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
