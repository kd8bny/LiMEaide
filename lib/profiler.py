import os
import re
import fnmatch
import contextlib
import json
from termcolor import colored, cprint


class Profiler(object):
    """Maintain and impliment precomiled modules and profiles."""

    def __init__(self):
        super(Profiler, self).__init__()
        self.profiles = []
        self.profiles_dir = './profiles/'
        self.manifest = 'manifest.json'

    def _clean_manifest(self):
        """Determine if profile need to be cleaned.

        Returns bool notifying the need to reload profiles.
        """
        num_profiles = len(fnmatch.filter(
            os.listdir(self.profiles_dir), 'lime-*.ko'))

        if num_profiles != len(self.profiles):
            print("Cleaning profile manifest")
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

        reload_profiles = self._clean_manifest()
        if reload_profiles:
            self.load_profiles()

    def create_profile(self, remote_session):
        """Create a new profile a save to manifest.

        Look through the output of uname and lsb_release to determine
        versions.
        """
        distro, kver, arch = '', '', ''
        if remote_session.get_file_stat('/etc/', 'os-release'):
            os_release = remote_session.exec_cmd(
                "cat /etc/{}".format('os-release'), False)

            d_id = list(filter(lambda val: 'ID=' in val, os_release))
            d_id = d_id[len(d_id) - 1].split('=')
            d_version = list(filter(lambda val: 'VERSION=' in val, os_release))
            d_version = d_version[0].split('=')
            distro = "{0}-{1}".format(d_id[1].lower(), d_version[1].lower())

        if not distro:
            releases = remote_session.exec_cmd("cd /etc/; ls *-release", False)
            releases = releases[0].split()
            if len(releases) >= 1:
                if 'lsb-release' in releases:
                    lsb_release = remote_session.exec_cmd(
                        "cat /etc/{}".format('lsb-release'), False)

                    d_id = list(filter(
                        lambda val: 'DISTRIB_ID' in val, lsb_release))
                    d_id = d_id[0].split('=')
                    distro = d_id[1].lower()

                else:
                    gen_release = remote_session.exec_cmd(
                        "cat /etc/{}".format(releases[0]), False)
                    distro = gen_release[0][:10]

        if not distro:
            distro = input(colored("Cannot determine distribution. Please " +
                                   "enter distribution name: ", 'red'))

        uname = remote_session.exec_cmd('uname -rm', False)
        kver, arch = uname[0].split()
        distro = re.sub('[^a-zA-Z0-9-_*.]', '', distro)

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
