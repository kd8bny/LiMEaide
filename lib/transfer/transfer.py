

class Transfer:
    """Top level parent. Override all functions when developing new
    mechanisms"""

    def __init__(self):
        pass

    def __transfer_status__(self, filename, bytes_so_far, bytes_total):
        # TDOD can we do this abstracted?
        """Callback to provide status of the files being transfered.

        Calling function must print new line on return or else line will be
        overwritten.
        """
        pass

    def pull(self, remote_dir, local_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        pass

    def put(self, local_dir, remote_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        pass

    def file_stat(self, remote_dir, filename):
        """Check to see if remote file exists and size is greater than 0.

        :param remote_dir Directory without filename
        :param filename File to Check
        :return If the file exists
        """
        pass

    def connect(self):
        pass

    def close(self):
        pass
