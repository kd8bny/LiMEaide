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
from termcolor import cprint


class Session:
    """Session will take care of all the backend communications."""

    def __init__(self, config, client, is_verbose=False):
        super(Session, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.client = client
        self.is_verbose = is_verbose

    def __error_check__(self, stdout):
        """Check for standard errors from stdout"""
        for line in stdout:
            if "error" in line.lower():
                self.logger.error(line)

                return True

        return False

    def __print__(self, stdout, err=False):
        stdout = [line.strip() for line in stdout]
        for line in stdout:
            if line and line != self.client.pass_:
                if not err:
                    self.logger.info(line)
                    if self.is_verbose:
                        print(line)
                else:
                    self.logger.error(line)
                    cprint(line, 'red')

    def check_integrity(self):
        BUFF_SIZE = 65536
        digest = hashlib.sha1()

        cprint("> Computing message digest of image", 'blue')
        with open(self.client.output_dir + self.client.output, 'rb') as f:
            while True:
                data = f.read(BUFF_SIZE)
                if not data:
                    break
                digest.update(data)
        sha1 = digest.hexdigest()

        with open(self.client.output_dir +
                  self.client.output + '.sha1', 'r') as f:
            remote_sha1 = f.read()

        if sha1 == remote_sha1:
            cprint("> Digest complete (sha1) {}".format(sha1), 'green')
        else:
            cprint("> DIGEST MISMATCH (sha1) \nlocal  {0} \nremote {1}".format(
                sha1, remote_sha1), 'red')

    def exec_cmd(self, cmd, priv=False, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param requires_privlege Does this command require elevated privileges
        :If command fails disconnect session
        :return stdout
        """
        pass

    def connect(self):
        """Call to set connection with remote client."""

        pass

    def disconnect(self):
        """Call to end session and remove files from remote client."""

        pass
