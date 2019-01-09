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

import logging
import shutil

from subprocess import Popen
from termcolor import cprint


class VolDeploy(object):
    """Develops Volatility profile to analyze RAM dump."""

    def __init__(self, config, session):
        super(VolDeploy, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.client = session.client
        self.session = session

        self.map = 'System.map-{}'.format(self.client.profile['kver'])

    def get_maps(self):
        """Grab system maps from remote client."""

        cprint("> Attempting to grab files for volatility profile", 'blue')
        cprint("> Obtaining system.map", 'blue')

        self.session.exec_cmd("cp /boot/{0} {1}".format(
            self.map, self.config.lime_rdir), priv=True,
            disconnect_on_fail=False)
        self.session.exec_cmd("chmod 744 {0}{1}".format(
            self.config.lime_rdir, self.map), priv=True)

        self.session.transfer.pull(
            self.config.lime_rdir, self.client.output_dir, self.map)

    def get_profile(self):
        """Obtain symbols from module and zip the profile."""

        cprint("> Obtaining symbols", 'blue')

        dwarf_file = open(
            self.client.output_dir + self.client.profile['kver'] +
            '.dwarf', 'w+')
        sp = Popen(
            ['dwarfdump', '-d', '-i',
                self.config.profile_dir + self.client.profile['module']],
            stdout=dwarf_file)
        sp.wait()
        dwarf_file.flush()

        pf = Popen(
            ['zip', '-j',
                self.client.output_dir + self.client.profile['profile'],
                self.client.output_dir +
                    self.client.profile['kver'] + '.dwarf',
                self.client.output_dir + self.map])
        pf.wait()

    def main(self, vol_dir):
        """Start building a Volatility profile."""

        self.get_maps()
        self.get_profile()

        if vol_dir != 'None':
            shutil.copy(
                self.client.output_dir + self.client.profile['profile'],
                vol_dir + self.client.profile['profile'])

        cprint("Profile generation complete run 'vol.py --info | " +
               "grep Linux' to see your profile", 'green', attrs=['blink'])
