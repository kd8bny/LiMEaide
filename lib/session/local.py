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

import sys
from subprocess import Popen, PIPE
from termcolor import colored, cprint
from lib.transfer import local
from lib.session.session import Session


class Local(Session):
    """Session will take care of all the backend communications."""

    def __init__(self, config, client, is_verbose=False):
        super(Local, self).__init__(config, client, is_verbose)

    def exec_cmd(self, cmd, priv=False, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param priv Does this command require elevated privileges
        :If command fails disconnect session
        :return stdout
        """
        popen = None
        stdout, stderr = None, None
        if self.client.user is not 'root' and priv:
            cmd = "sudo -S -p ' ' {0}".format(cmd)
            popen = Popen(
                cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = popen.communicate(
                bytes(self.client.pass_, 'utf-8'))
        else:
            popen = Popen(
                cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = popen.communicate()

        output = stdout.decode('utf-8')
        output = output.split("\n")

        self.logger.info("Command executed: {0}".format(cmd))

        if self.__error_check__(output):
            self.__print__(output, err=True)
            cprint("Error deploying LiMEaide :(", 'red')
        else:
            self.__print__(output)

        error = stderr.decode('utf-8')
        error = error.split("\n")

        if error:
            self.__print__(error, err=True)
            cprint("Error deploying LiMEaide :(", 'red')

            if disconnect_on_fail:
                self.disconnect()
                sys.exit()

        return output

    def connect(self):
        """Call to set connection with remote client."""
        self.transfer = local.Local()
        self.transfer.connect()

    def disconnect(self):
        """Call to end session and remove files from remote client."""
        cprint("> Cleaning up...", 'blue')
        if self.transfer.file_stat(self.config.lime_rdir, ''):
            self.exec_cmd('rm -rf {0}'.format(
                self.config.lime_rdir), True, False)

        if self.exec_cmd("lsmod | grep lime"):
            cprint("> Removing LKM...standby", 'blue')
            self.exec_cmd('rmmod lime.ko', True, False)

        self.transfer.close()
