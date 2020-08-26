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
import sys

from termcolor import colored, cprint


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

    def check_constraints(self):
        """Check available space on client. If space isn't available suggest
        alternative transfer method.
        """

        stdout = self.session.exec_cmd(
            "free -b | awk '/^Mem/ {print($2);}'", disconnect_on_fail=False)
        ram_size = int(int(stdout[0]) / float(1 << 20))

        stdout = self.session.exec_cmd(
            """df . | awk '{if ($4 != "Available") print($4);}'""",
            disconnect_on_fail=False)
        disk_free = int(int(stdout[0]) / float(1 << 10))

        if not self.client.port:
            if ram_size > disk_free:
                self.logger.error("Insufficient disk space to capture memory")
                cprint("> Image will occupy approximately " +
                       "{0} of {1} MiB available".format(
                           ram_size, disk_free), 'green')
                sys.exit(colored(
                    "Insufficient Disk space to capture memory. " +
                    "Try using the -s option for network transfer", 'red'))
            else:
                cprint("> Image will occupy approximately " +
                       "{0} of {1} MiB available".format(
                           ram_size, disk_free), 'green')
        else:
            cprint("> Image will occupy approximately {0} MiB".format(
                ram_size), 'green')

    def send_lime(self):
        """Send LiME to remote client. Uses pre-compiled module if supplied."""

        cprint("> Sending LiME src to remote client", 'blue')
        lime_src = ['main.c', 'disk.c', 'tcp.c', 'hash.c', 'deflate.c',
                    'lime.h', 'Makefile']

        self.session.exec_cmd(
            "mkdir -p {}".format(self.config.lime_rdir))

        # Generate information to create a new profile
        if self.new_profile:
            for file in lime_src:
                self.session.transfer.put(
                    self.config.lime_dir, self.config.lime_rdir, file)

            self.client.profile = self.profiler.create_profile(
                self.session)

            cprint("> Building loadable kernel module", 'blue')
            self.session.exec_cmd(
                "cd {}; make symbols".format(
                    self.config.lime_rdir), disconnect_on_fail=False)
            self.session.exec_cmd("mv {0}lime-{1}.ko {0}{2}".format(
                self.config.lime_rdir, self.client.profile["kver"],
                self.client.profile["module"]))

            self.logger.info(
                "new profile created {0}".format(
                    self.client.profile["module"]))

        # Use an old profile
        else:
            self.session.transfer.put(
                self.config.profile_dir, self.config.lime_rdir,
                self.client.profile["module"])

            self.logger.info(
                "Old profile used {0}".format(self.client.profile["module"]))
        cprint("> Detected {0} {1} {2}".format(
            self.client.profile["distro"], self.client.profile["kver"],
            self.client.profile["arch"]), 'blue')

    def __build_lime_args__(self):
        """Build the LiME arguments"""

        path = "path="
        format = "format={}".format(self.client.format)
        digest = ""
        compress = ""

        if self.client.digest:
            digest = "digest={}".format(self.client.digest)
        if self.client.zlib:
            compress = "compress=1"

        if self.client.port:
            path += "tcp:{0}".format(self.client.port)
        else:
            path += "{0}{1}".format(
                self.config.lime_rdir, self.client.output)

        lime_args = "{0} {1} {2} {3}".format(path, format, digest, compress)

        cprint("> LiME arguments: {}".format(lime_args), 'blue')

        return lime_args


    def install_lime(self):
        """Will install LiME and page virtual memory."""

        cprint("> Installing LiME and paging virtual memory", 'blue')
        lime_args = self.__build_lime_args__()

        # Determine xfer method based on if the port is declared
        if self.client.port:
            self.__install_lime_sock__(lime_args)
        else:
            self.__install_lime__(lime_args)


    def __install_lime_sock__(self, lime_args):
        """Install LiME and connect to the open socket."""

        cmd = "insmod {0}{1} '{2}'".format(
            self.config.lime_rdir, self.client.profile["module"], 
            lime_args)

        # Open Socket
        self.transfer_image()
        self.session.exec_cmd(cmd, priv=True)
        self.logger.info("LiME installed")

    def __install_lime__(self, lime_args):
        """Install LiME and transfer with SFTP."""

        cmd = "insmod {0}{1} '{2}'".format(
            self.config.lime_rdir, self.client.profile["module"],
            lime_args)

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
        os.symlink('../.' + self.config.log_dir + self.config.date + '.log',
                   self.client.output_dir + self.config.date + '.log')

        if self.client.port:
            self.__transfer_image_sock__()
        else:
            self.__transfer_image__()

        if self.new_profile:
            self.session.transfer.pull(
                self.config.lime_rdir, self.config.profile_dir,
                self.client.profile['module'])

    def __transfer_image_sock__(self):
        """Retrieve files over TCP."""

        remote_file = self.client.output
        remote_file_hash = "{}.{}".format(
            self.client.output, self.client.digest)

        self.session.transfer.pull(
            None, self.client.output_dir, remote_file)

        if self.client.digest:
            self.session.transfer.pull(
                None, self.client.output_dir, remote_file_hash)

    def __transfer_image__(self):
        """Retrieve files with SFTP."""

        remote_file = self.client.output
        remote_file_hash = "{}.{}".format(
            self.client.output, self.client.digest)

        self.session.transfer.pull(
            self.config.lime_rdir, self.client.output_dir, remote_file)

        if self.client.digest:
            self.session.transfer.pull(
                self.config.lime_rdir, self.client.output_dir,
                remote_file_hash)

    def deploy(self):
        """Begin the process of transporting LiME and dumping the RAM."""

        if self.client.profile is None:
            self.new_profile = True

        self.check_constraints()
        self.send_lime()
        self.install_lime()
        self.session.check_integrity()

        cprint("> Memory extraction is complete", 'blue')
        cprint("{0} is in {1}".format(
            self.client.output, self.client.output_dir), 'cyan')
