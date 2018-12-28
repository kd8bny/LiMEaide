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
import os
from termcolor import cprint


class LimeDeploy(object):
    """Send LiME and retrieve the RAM dump from a remote client."""

    def __init__(self, config, session, profiler):
        super(LimeDeploy, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session
        self.client = session.client
        self.profiler = profiler

        self.new_profile = False

    def send_lime(self):
        """Send LiME to remote client. Uses pre-compiled module if supplied."""
        cprint("> Sending LiME src to remote client", 'blue')
        lime_src = ['main.c', 'disk.c', 'tcp.c', 'hash.c', 'lime.h',
                    'Makefile']

        self.session.exec_cmd(
            'mkdir -p {}'.format(self.config.lime_rdir))

        # Generate information to create a new profile
        if self.new_profile:
            for file in lime_src:
                self.session.transfer.put(
                    self.config.lime_dir, self.config.lime_rdir, file)

            self.client.profile = self.profiler.create_profile(
                self.session)
            print(self.client.profile["module"])

            cprint("> Building loadable kernel module", 'blue')
            self.session.exec_cmd(
                'cd {}; make debug'.format(self.config.lime_rdir))
            self.session.exec_cmd("mv {0}lime-{1}.ko {0}{2}".format(
                self.config.lime_rdir, self.client.profile["kver"],
                self.client.profile["module"]))

            self.logger.info(
                "new profile created {0}".format(
                    self.client.profile["module"]))

        # Use an old profile
        else:
            self.session.transfer.put(
                self.profiles_dir, self.config.lime_rdir,
                self.client.profile["module"])

            self.logger.info(
                "Old profile used {0}".format(self.client.profile["module"]))
        cprint("> Detected {0} {1} {2}".format(
            self.client.profile["distro"], self.client.profile["kver"],
            self.client.profile["arch"]), 'blue')

    def install_lime(self):
        """Will install LiME and dump RAM."""
        cprint("> Installing LiME and retrieving RAM", 'blue')

        # Build the correct instructions
        path = "path="
        format = "format={}".format(self.client.format)
        digest = ""

        if self.client.digest:
            digest = "digest={}".format(self.client.digest)

        if self.client.port:
            path += "tcp:{0}".format(self.client.port)
            self.__install_lime_sock__(path, format, digest)
        else:
            path += "{0}{1}".format(
                self.config.lime_rdir, self.client.output)
            self.__install_lime__(path, format, digest)

    def __install_lime_sock__(self, path, format, digest):
        cprint(">> {}".format(path), 'blue')
        cprint(">> {}".format(format), 'blue')
        cprint(">> {}".format(digest), 'blue')

        cmd = "insmod {0}{1} '{2} {3} {4}'".format(
            self.config.lime_rdir, self.client.profile["module"],
            path, format, digest)

        # Open Socket
        self.transfer_image()
        self.logger.info("LiME installing")
        self.session.exec_cmd(cmd, priv=True)

        # TODO check the queue for transfer

    def __install_lime__(self, path, format, digest):
        cprint(">> {}".format(path), 'blue')
        cprint(">> {}".format(format), 'blue')
        cprint(">> {}".format(digest), 'blue')

        cmd = "insmod {0}{1} '{2} {3} {4}'".format(
            self.config.lime_rdir, self.client.profile["module"],
            path, format, digest)

        self.session.exec_cmd(cmd, priv=True)
        self.logger.info("LiME installed")

        cprint("> Changing permissions", 'blue')
        self.session.exec_cmd(
            "chmod 755 {0}{1}".format(
                self.config.lime_rdir, self.client.output), priv=True)

        self.transfer_image()

    def transfer_image(self):
        """Retrieve files from remote client."""
        cprint("> Beam me up Scotty", 'blue')
        os.mkdir(self.client.output_dir)
        # TODO Sym link logs

        if self.client.port:
            self.__transfer_image_sock__()
        else:
            self.__transfer_image__()

        if self.new_profile:
            self.session.transfer.pull(
                self.config.lime_rdir, self.config.profile_dir,
                self.client.profile['module'])

    def __transfer_image_sock__(self):
        remote_file = self.client.output
        remote_file_hash = "{}.{}".format(
            self.client.output, self.client.digest)

        self.session.transfer.pull(
            None, self.client.output_dir, remote_file)

        if self.client.digest:
            self.session.transfer.pull(
                None, self.client.output_dir, remote_file_hash)

    def __transfer_image__(self):
        remote_file = self.client.output
        remote_file_hash = "{}.{}".format(
            self.client.output, self.client.digest)

        self.session.transfer.pull(
            self.config.lime_rdir, self.client.output_dir, remote_file)

        if self.client.digest:
            self.session.transfer.pull(
                self.config.lime_rdir, self.client.output_dir, remote_file_hash)

    def main(self):
        """Begin the process of transporting LiME and dumping the RAM."""
        if self.client.profile is None:
            self.new_profile = True

        self.send_lime()
        self.install_lime()

        if self.client.delay_pickup:
            self.transfer_image()
        # self.check_integrity()

        cprint("> Memory extraction is complete", 'blue')
        cprint("{0} is in {1}".format(
            self.client.output, self.client.output_dir), 'cyan')
