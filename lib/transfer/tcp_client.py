import socket
import sys
import logging


class TCP_CLIENT:
    """docstring for TCP_CLIENT"""

    def __init__(self, ip, port, output):
        super(TCP_CLIENT, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        self.output = output

    def __handle_client__(self, sock):
        while True:
            file_buffer = b''
            data = sock.recv(4096)
            if data:
                file_buffer += data
            else:
                break

            self.__write_out__(file_buffer)

        return True

    def __write_out__(self, data):
        try:
            with open(self.output, 'ab') as f:
                f.write(data)

        except Exception as e:
            self.logger.error("Unable to save output: {}".format(e))
            sys.exit("Unable to save output")

    def connect(self):
        self.logger.info("Connecting to Socket")
        while True:
            try:
                srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srv.connect((self.ip, self.port))

                complete = self.__handle_client__(srv)

                if complete:
                    break

            except socket.error as e:
                pass

            finally:
                srv.close()
