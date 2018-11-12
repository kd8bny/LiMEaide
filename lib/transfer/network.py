import functools
from lib.transfer.transfer import Transfer, TCP_CLIENT


class Network(Transfer):
    """Network transfer method using SFTP or raw TCP"""

    def __init__(self, paramiko_session, method, ip=None, port=None):
        Transfer.__init__(self, paramiko_session)
        self.complete_percent = []
        #self.SFTP = None
        self.ip = ip
        self.port = port

    def pull(self, *args):
        """This is a raw pull, create a TCP server.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        if self.paramiko_session.client
        self.pull_tcp()

    def pull_tcp(self, local_dir, filename):
        """Called when data needs to be pulled from remote system.
            Connects as a TCP client

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        TCP_CLIENT(self.ip, self.port, local_dir, filename)

    def pull_sftp(self, remote_dir, local_dir, filename):
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
        self.SFTP = self.remote_session.open_sftp()

    def close(self):
        # TODO Catch error
        self.remote_session.close()
