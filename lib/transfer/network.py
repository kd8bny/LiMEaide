import functools
from threading import Event, Thread

from lib.transfer.transfer import Transfer
from lib.transfer.tcp_client import TCP_CLIENT


class Network(Transfer):
    """Network transfer method using SFTP or raw TCP"""

    def __init__(self, paramiko_session, ip=None, port=None):
        Transfer.__init__(self)
        self.paramiko_session = paramiko_session
        self.ip = ip
        self.port = port
        # self.complete_percent = []
        # self.SFTP = None

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
        client = TCP_CLIENT(ip, port, output)
        thread = Thread(target=client.connect)
        thread.start()

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
        self.paramiko_session.close()
