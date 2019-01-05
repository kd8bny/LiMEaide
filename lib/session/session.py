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
import hashlib
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

    def __print__(self, text, err=False):
        for line in text:
            if self.client.pass_ not in text:
                if not err:
                    if self.is_verbose:
                        print(line)
                else:
                    cprint(line, 'red')

    def check_integrity(self):
        BUFF_SIZE = 65536
        digest = hashlib.new(self.client.digest)

        cprint("> Computing message digest of image", 'blue')
        with open(self.client.output_dir + self.client.output, 'rb') as f:
            while True:
                data = f.read(BUFF_SIZE)
                if not data:
                    break
                digest.update(data)
        hash = digest.hexdigest()

        with open(self.client.output_dir +
                  self.client.output + '.' + self.client.digest, 'r') as f:
            remote_hash = f.read()

        if hash == remote_hash:
            cprint("> Digest complete {0} {1}".format(
                self.client.digest, hash), 'green')
        else:
            cprint("> DIGEST MISMATCH {0} \nlocal  {1} \nremote {2}".format(
                self.client.digest, hash, remote_hash), 'red')

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
