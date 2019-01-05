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
import paramiko
from termcolor import colored, cprint
from lib.transfer import network
from lib.session.session import Session


class Network(Session):
    """Session will take care of all the backend communications."""

    def __init__(self, config, client, is_verbose=False):
        Session.__init__(self, config, client, is_verbose)
        self.paramiko_session = None
        self.transfer = None

    def exec_cmd(self, cmd, priv=False, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param requires_privlege Does this command require elevated privileges
        :If command fails disconnect session
        :return stdout
        """
        stdout, stderr = None, None
        if self.client.user is not 'root' and priv:
            cmd = "sudo -S -p ' ' {0}".format(cmd)
            stdin, stdout, stderr = self.paramiko_session.exec_command(
                cmd, get_pty=True)
            stdin.write(self.client.pass_ + '\n')
            stdin.flush()
        else:
            stdin, stdout, stderr = self.paramiko_session.exec_command(
                cmd, get_pty=True)

        lstdout = stdout.readlines()
        output = []
        if lstdout:
            for line in lstdout:
                line.strip('\r\n')
                output += line.split()

        self.logger.info("Command executed: {0}".format(cmd))

        if self.__error_check__(lstdout):
            self.__print__(lstdout, err=True)
            self.logger.error(lstdout)

            if disconnect_on_fail:
                self.disconnect()
                sys.exit(colored("Error deploying LiMEaide :(", 'red'))
            else:
                cprint("Non-fatal error - continuing", 'magenta')

        else:
            self.__print__(output)
            self.logger.info(lstdout)

        error = stdout.readlines()

        if error:
            self.__print__(error, err=True)
            self.logger.error(lstdout)

            if disconnect_on_fail:
                self.disconnect()
                sys.exit(colored("Error deploying LiMEaide :(", 'red'))
            else:
                cprint("Non-fatal error - continuing", 'magenta')

        return output

    def connect(self):
        """Call to set connection with remote client."""

        try:
            self.paramiko_session = paramiko.SSHClient()
            self.paramiko_session.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())

            self.paramiko_session.connect(
                self.client.ip, username=self.client.user,
                password=self.client.pass_, key_filename=self.client.key,
                allow_agent=True)

        except (paramiko.AuthenticationException,
                paramiko.ssh_exception.NoValidConnectionsError) as e:
            self.logger.error(e)
            sys.exit(colored("> {}".format(e), 'red'))

        except paramiko.SSHException as e:
            self.logger.error(e)
            sys.exit(colored("> {}".format(e), 'red'))

        self.transfer = network.Network(
            self.paramiko_session, self.client.ip, self.client.port)
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
