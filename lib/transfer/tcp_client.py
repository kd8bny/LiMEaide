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

import socket
import sys
import logging
import threading
import time


class TCP_CLIENT(threading.Thread):
    """docstring for TCP_CLIENT"""

    def __init__(self, ip, port, output):
        super(TCP_CLIENT, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        self.output = output

        self.timeout = 2

    def __handle_client__(self, sock):
        buffer_size = 4096

        while True:
            file_buffer = b''
            data = sock.recv(buffer_size)
            if data:
                file_buffer += data
            else:
                break

            self.__write_out__(file_buffer)

    def __write_out__(self, data):
        try:
            with open(self.output, 'ab') as f:
                f.write(data)

        except Exception as e:
            self.logger.error("Unable to save output: {}".format(e))
            sys.exit("Unable to save output")

    def connect(self):
        self.logger.info("Connecting to Socket")
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.connect((self.ip, self.port))

            self.logger.info("Connection Successful")

            self.__handle_client__(srv)

        except ConnectionRefusedError as e:
            return True

        except socket.error as e:
            self.logger.error(e)
            # Exit application, failed transfer

        finally:
            self.logger.info("Socket Closed")
            srv.close()

        return False

    def run(self):
        retry = True
        # timeout
        while retry:
            retry = self.connect()
            time.sleep(self.timeout)
            # Event timeout
