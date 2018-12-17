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

        self.timeout = 10

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
        self.logger.info("File saved")

    def __write_out__(self, data):
        try:
            with open(self.output, 'ab') as f:
                f.write(data)

        except Exception as e:
            self.logger.error("Unable to save output: {}".format(e))
            # TODO this is a thread, doesnt kill main
            sys.exit("Unable to save output")

    def __connect__(self):
        self.logger.info("Connecting to Socket")
        retry = False
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setblocking(False)
            srv.connect((self.ip, self.port))

            self.logger.info("Connection Successful")

            self.__handle_client__(srv)

        except ConnectionRefusedError as e:
            retry = True
            #return True

        except socket.error as e:
            print(e)
            retry = True
            self.logger.error(e)
            # Exit application, failed transfer

        finally:
            self.logger.info("Socket Closed")
            srv.shutdown(socket.SHUT_RDWR)
            print(srv.close())
        return retry

    def run(self):
        retry = True

        while retry:
            time.sleep(self.timeout)
            self.logger.info("Failed Connection, retrying")
            retry = self.__connect__()
            # TODO Event timeout

        print("thread compte")


class CONNECTION_MANAGER(threading.Thread):
    """docstring for TCP_CLIENT"""

    def __init__(self, q, e):
        super(CONNECTION_MANAGER, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.event_kill = e
        self.queue = q

    def __start_client__(self, conn):
        client = TCP_CLIENT(conn[0], conn[1], conn[2])
        client.start()
        client.join()

    def run(self):
        while not self.event_kill.is_set():
            time.sleep(3)
            if self.queue.empty():
                continue
            else:
                print(self.queue)
                connection = self.queue.get()
                print(connection)
                self.__start_client__(connection)
