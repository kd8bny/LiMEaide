import os
import shutil


class Local(Transfer):
    """Session will take care of all the backend communications."""

    def __init__(self):
        super(Local, self).__init__()
        pass


    def pull(self, remote_dir, local_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        if self.file_stat(remote_dir, filename):
        shutil.move(remote_dir + filename, local_dir + filename)

        return

    def put(self, local_dir, remote_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        shutil.move(local_dir + filename, remote_dir + filename)

        return


    def file_stat(self, remote_dir, filename):
        """Check to see if remote file exists and size is greater than 0.

        :param remote_dir Directory without filename
        :param filename File to Check
        :return If the file exists
        """
        file_exists = False

        try:
            os.stat(remote_dir + filename)

        except IOError as e:
            self.logger.warning(e)

        return file_exists
