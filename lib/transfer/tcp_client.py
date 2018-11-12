import socket
import sys
import logging


class TCP_CLIENT:
    """docstring for TCP_CLIENT"""

    def __init__(self, ip, port, local_dir, file_name):
        super(TCP_CLIENT, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        self.file_name = local_dir + file_name

    def __handle_client__(self, sock):
        while True:
            file_buffer = b''
            data = sock.recv(4096)
            if data:
                file_buffer += data
            else:
                break

            self.__write_out__(file_buffer)

    def __write_out__(self, data):
        try:
            with open(self.file_name, 'ab') as f:
                f.write(data)

        except as e:
            self.logger.error("Unable to save output: {}".format(e))
            sys.exit()

    def main(self):
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.connect((self.ip, self.port))

            self.__handle_client__(srv)

        except socket.error as e:
            sys.exit(e)

        finally:
            srv.close()
