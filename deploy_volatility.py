import sys
from subprocess import Popen


class VolDeploy(object):
    """Develops Volatility profile to analyze RAM dump."""

    def __init__(self, session):
        super(VolDeploy, self).__init__()
        self.client = session.client_
        self.remote_session = session

        self.output_dir = './profiles/'
        self.lime_rdir = '/tmp/lime/'
        self.map = 'System.map-%s' % self.client.profile['kver']

    def get_maps(self):
        """Grab system maps from remote client."""
        print("Attempting to grab files for volatility profile")
        print("Obtaining System.maps")
        self.remote_session.exec_cmd(
            "cp /boot/{0} {1}".format(self.map, self.lime_rdir), True)
        self.remote_session.exec_cmd(
            "chmod 744 {0}{1}".format(self.lime_rdir, self.map), True)
        error = self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, self.map)

        if error:
            sys.exit("Map not found cannot build profile")

        print("done.")

    def get_profile(self):
        """Obtain symbols from module and zip the profile."""
        print("Obtaining symbols")
        dwarf_file = open(
            self.client.output_dir + self.client.profile['kver'] +
            '.dwarf', 'w+')
        sp = Popen(
            ['dwarfdump', '-d', '-i',
             self.output_dir + self.client.profile['module']],
            stdout=dwarf_file)
        sp.wait()
        dwarf_file.flush()

        Popen(
            ['zip', '-j', self.output_dir + self.client.profile['profile'],
             self.client.output_dir + self.client.profile['kver'] + '.dwarf',
             self.client.output_dir + self.map])
        print("done.")

    def main(self, vol_path):
        """Start building a Volatility profile."""
        if vol_path != 'None':
            self.output_dir = vol_path
        self.get_maps()
        self.get_profile()
