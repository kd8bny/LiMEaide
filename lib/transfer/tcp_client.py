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
import time
import threading
import selectors
import socket
import struct
import sys
from termcolor import colored
from queue import Queue


class TCP_CLIENT(threading.Thread):
    """docstring for TCP_CLIENT"""

    def __init__(self, qresult, ip, port, output):
        super(TCP_CLIENT, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.qresult = qresult
        self.ip = ip
        self.port = port
        self.output = output

        self.result = {'success': True, 'terminal': False}
        self.byte_count = 0

    def __transfer_status__(self, bytes_len):
        """Callback to provide status of the files being transfered.
        Calling function must print new line on return or else line will be
        overwritten.
        """
        self.byte_count += bytes_len
        print(colored(
            "Transfer of {0} is at {1:d} bytes".format(
                self.output, self.byte_count), 'cyan'), end='\r', flush=True)

    def __write_out__(self, data):
        try:
            with open(self.output, 'ab') as f:
                f.write(data)

        except Exception as e:
            self.logger.error("Unable to save output: {}".format(e))
            self.result['success'] = False
            self.result['terminal'] = True
            sys.exit("Unable to save output")

    def __handle_client__(self, key, mask, sel):
        retry = True
        sock = key.fileobj

        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)

                if recv_data:
                    self.__transfer_status__(len(recv_data))
                    self.__write_out__(recv_data)
                else:
                    self.logger.info("File saved")
                    retry = False

            except socket.error as e:
                self.logger.error(e)
                self.result['success'] = False
                retry = False

        return retry

    def run(self):
        retry = True

        self.logger.info("Connecting to Socket")
        sel = selectors.DefaultSelector()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.setsockopt(
            socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        conn.setblocking(False)

        conn.connect_ex((self.ip, self.port))
        sel.register(conn, selectors.EVENT_READ, data=None)

        while retry:
            events = sel.select()
            for key, mask in events:
                retry = self.__handle_client__(key, mask, sel)

        sel.unregister(conn)
        if self.result['success']:
            conn.shutdown(socket.SHUT_RDWR)

        self.qresult.put(self.result)
        self.logger.info("Socket Closed")


class CONNECTION_MANAGER(threading.Thread):
    """docstring for CONNECTION_MANAGER"""

    def __init__(self, q, e):
        super(CONNECTION_MANAGER, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.event_kill = e
        self.queue = q

        self.qstatus = Queue()
        self.retry_count = 0

    def __start_client__(self, conn):
        client = TCP_CLIENT(self.qstatus, conn[0], conn[1], conn[2])
        client.start()
        client.join()

    def run(self):
        while not self.event_kill.is_set():
            time.sleep(3)
            if self.queue.empty():
                continue
            else:
                connection = self.queue.get()
                self.__start_client__(connection)
                status = self.qstatus.get()

                if not status['success']:
                    if status['terminal']:
                        self.logger.warning(
                            "Failed connection, closing down")
                        self.event_kill.set()

                    elif self.retry_count > 4:
                        self.logger.warning(
                            "Retry count exceeded, closing down")
                        self.event_kill.set()

                    else:
                        self.retry_count += 1
                        self.logger.warning(
                            "connection failed, adding back to queue")
                        self.queue.put(connection)

        self.logger.info("Connection manager is finished")


if __name__ == '__main__':
    kill_conn_man = threading.Event()
    queue = Queue()
    conn_man = CONNECTION_MANAGER(queue, kill_conn_man)
    conn_man.start()
    queue.put(['192.168.1.17', 1337, "test2"])
    conn_man.join()
