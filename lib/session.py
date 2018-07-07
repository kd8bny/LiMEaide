import sys
import functools
import logging
import paramiko
import hashlib
from termcolor import colored, cprint


class Session(object):
    """Session will take care of all the backend communications."""

    def __init__(self, client, is_verbose=False):
        super(Session, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.client_ = client
        self.is_verbose = is_verbose
        self.session = None
        self.SFTP = None

        self.complete_percent = []

    def __error_check__(self, stdout):
        """Check for standard errors from stdout"""
        for line in stdout:
            if "error" in line.lower():
                self.logger.error(line)
                return 1

        return 0

    def __calc_hash(self, filename):
        """Calculate sha256 hash of file. 

        :param filename Path to file
        """
        file_hash = hashlib.sha256()
        with open(filename, "rb") as binary_file:
            for file_chunk in iter(lambda: binary_file.read(4096), b""):
              file_hash.update(file_chunk)
            
        return file_hash.hexdigest()

    def __log_file_details(self, filename):
        """Log details of file prior to transfer to target host 

        :param filename Path to file
        """
        try:
            file_hash = self.__calc_hash(filename)
            self.logger.info("File Transmit Details: {0} (sha256={1})".format(
                filename, file_hash))
        except Exception as e:
            cprint("Warning: Error calculating file checksum", 'red')
            self.logger.warning("Error calculating file checksum: {0}".format(
                filename))
            self.logger.warning(e)

    def __transfer_status__(self, filename, bytes_so_far, bytes_total):
        """Callback to provide status of the files being transfered.

        Calling function must print new line on return or else line will be
        overwritten.
        """
        percent = int(100 * bytes_so_far / bytes_total)
        if percent % 10 == 0 and percent not in self.complete_percent:
            self.complete_percent.append(percent)
            print(
                colored("Transfer of %r is at %d/%d bytes (%.0f%%)\r"
                   % (filename, bytes_so_far, bytes_total, percent), 'cyan'), end='\r', flush=True)

    def exec_cmd(self, cmd, requires_privlege, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param requires_privlege Does this command require elevated privileges
        :return stdout
        """
        stdout, stderr = None, None
        if self.client_.is_sudoer and requires_privlege:
            cmd = "sudo -S -p ' ' {0}".format(cmd)
            self.logger.info("Command executed: {0}".format(cmd))
            stdin, stdout, stderr = self.session.exec_command(
                cmd, get_pty=True)
            stdin.write(self.client_.pass_ + '\n')
            stdin.flush()
        else:
            self.logger.info("Command executed: {0}".format(cmd))
            stdin, stdout, stderr = self.session.exec_command(
                cmd, get_pty=True)

        stdout = [line.strip() for line in stdout]
        for line in stdout:
            if line and line != self.client_.pass_:
                self.logger.info(line)
                if self.is_verbose:
                    print(line)

        if not stderr or self.__error_check__(stdout):
            for line in stderr:
                self.logger.error(line)
                print(line.strip('\n'))
            cprint("Error deploying LiMEaide :(", 'red')

            if disconnect_on_fail:
                self.disconnect()
                sys.exit()

        return stdout

    def pull_sftp(self, remote_dir, local_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """

        self.complete_percent = []
        if self.get_file_stat(remote_dir, filename):
            status = functools.partial(self.__transfer_status__, filename)
            self.SFTP.get(
                remote_dir + filename, local_dir + filename, callback=status)
            print('\n')

    def put_sftp(self, local_dir, remote_dir, filename):
        """Called when data needs to be transfered to remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir path to output dir on local machine
        :param filename file to transfer
        """
        # Calcuate and log file details prior to transfer
        self.__log_file_details(local_dir + filename)

        self.SFTP.put(local_dir + filename, remote_dir + filename)

    def get_file_stat(self, remote_dir, filename):
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

    def disconnect(self):
        """Call to end session and remove files from remote client."""
        cprint("> Cleaning up...", 'blue')
        self.exec_cmd('rm -rf ./.limeaide/', True, False)

        cprint("> Removing LKM...standby", 'blue')
        self.exec_cmd('rmmod lime.ko', True, False)

        self.SFTP.close()
        cprint("> Done", 'green')

    def connect(self):
        """Call to set connection with remote client."""
        try:
            self.session = paramiko.SSHClient()
            self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.session.connect(
                self.client_.ip, username=self.client_.user,
                password=self.client_.pass_)

            self.SFTP = self.session.open_sftp()

        except (paramiko.AuthenticationException,
                paramiko.ssh_exception.NoValidConnectionsError) as e:
            print(colored("> {}".format(e), 'red'))
            self.logger.error(e)
            sys.exit()
