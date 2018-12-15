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

import functools
from threading import Event, Thread

from lib.transfer.transfer import Transfer
from lib.transfer.tcp_client import CONNECTION_MANAGER


class Network(Transfer):
    """Network transfer method using SFTP or raw TCP"""

    def __init__(self, paramiko_session, ip=None, port=None):
        Transfer.__init__(self)
        self.paramiko_session = paramiko_session
        self.ip = ip
        self.port = port

        self.conn_man = None

    def pull(self, remote_dir, local_dir, filename):
        """This is a raw pull, create a TCP server.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        if remote_dir is None:
            self.__pull_tcp__(self.ip, self.port, local_dir, filename)
        else:
            self.__pull_sftp__(remote_dir, local_dir, filename)

    def __pull_tcp__(self, ip, port, local_dir, filename):
        """Called when data needs to be pulled from remote system.
            Connects as a TCP client

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        output = local_dir + filename

        if not self.conn_man:
            self.conn_man = CONNECTION_MANAGER()
            self.conn_man.start()

        self.conn_man.add_connection(ip, port, output)

    def __pull_sftp__(self, remote_dir, local_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """

        self.complete_percent = []
        if self.file_stat(remote_dir, filename):
            status = functools.partial(self.__transfer_status__, filename)
            self.SFTP.get(
                remote_dir + filename, local_dir + filename, callback=status)
            print('\n')

    def put(self, local_dir, remote_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        self.SFTP.put(local_dir + filename, remote_dir + filename)

        return

    def file_stat(self, remote_dir, filename):
        """Check to see if remote file exists and size is greater than 0.

        :param remote_dir Directory without filename
        :param filename File to Check
        :return If the file exists
        """
        file_exists = False

        try:
            attributes = self.SFTP.stat(remote_dir + filename)
            if attributes.st_size > 0:
                file_exists = True

        except IOError as e:
            self.logger.warning(e)

        return file_exists

    def connect(self):
        # TODO Catch error
        self.SFTP = self.paramiko_session.open_sftp()

    def close(self):
        # TODO Catch error
        # TODO check threads
        self.paramiko_session.close()

        if self.conn_man:
            self.conn_man.kill()
            self.conn_man.join()
            self.logger.info("Connection Manager closed")
