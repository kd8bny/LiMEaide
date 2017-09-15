import sys
import shutil
from subprocess import Popen
from termcolor import colored, cprint


class VolDeploy(object):
    """Develops Volatility profile to analyze RAM dump."""

    def __init__(self, session):
        super(VolDeploy, self).__init__()
        self.client = session.client_
        self.remote_session = session

        self.output_dir = './profiles/'
        self.lime_rdir = './.limeaide/'
        self.map = 'System.map-%s' % self.client.profile['kver']

    def get_maps(self):
        """Grab system maps from remote client."""
        cprint("> Attempting to grab files for volatility profile", 'blue')
        cprint("> Obtaining system.map", 'blue')
        self.remote_session.exec_cmd(
            "cp /boot/{0} {1}".format(self.map, self.lime_rdir), True)
        self.remote_session.exec_cmd(
            "chmod 744 {0}{1}".format(self.lime_rdir, self.map), True)
        self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, self.map)

    def get_profile(self):
        """Obtain symbols from module and zip the profile."""
        cprint("> Obtaining symbols", 'blue')
        dwarf_file = open(
            self.client.output_dir + self.client.profile['kver'] +
            '.dwarf', 'w+')
        sp = Popen(
            ['dwarfdump', '-d', '-i',
             self.output_dir + self.client.profile['module']],
            stdout=dwarf_file)
        sp.wait()
        dwarf_file.flush()

        pf = Popen(
            ['zip', '-j', self.output_dir + self.client.profile['profile'],
             self.client.output_dir + self.client.profile['kver'] + '.dwarf',
             self.client.output_dir + self.map])
        pf.wait()

    def main(self, vol_dir):
        """Start building a Volatility profile."""
        self.get_maps()
        self.get_profile()

        if vol_dir != 'None':
            shutil.copy(self.output_dir +
                        self.client.profile['profile'], vol_dir +
                        self.client.profile['profile'])
        cprint("Profile generation complete run 'vol.py --info | " +
               "grep Linux' to see your profile", 'green', attrs=['blink'])
