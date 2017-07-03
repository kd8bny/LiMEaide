import sys
import functools
import paramiko
from termcolor import colored, cprint


class Session(object):
    """Session will take care of all the backend communications."""

    def __init__(self, client):
        super(Session, self).__init__()
        self.client_ = client
        self.session = None
        self.SFTP = None

        self.complete_percent = []

    @staticmethod
    def __error_check__(stdout):
        """Check for standard errors from stdout"""
        for line in stdout:
            if "error" in line.lower():
                return 1

        return 0

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

    def exec_cmd(self, cmd, requires_privlege):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param requires_privlege Does this command require elivated privledge
        :return stdout
        """
        stdout, stderr = None, None
        if self.client_.is_sudoer and requires_privlege:
            stdin, stdout, stderr = self.session.exec_command(
                "sudo -S -p ' ' {0}".format(cmd), get_pty=True)
            stdin.write(self.client_.pass_ + '\n')
            stdin.flush()
        else:
            stdin, stdout, stderr = self.session.exec_command(
                cmd, get_pty=True)

        stdout = [line.strip('\n\r') for line in stdout]
        for line in stdout:
            if line != self.client_.pass_:
                print(line)

        if not stderr or self.__error_check__(stdout):
            [print(line.strip('\n')) for line in stderr]
            sys.exit("Error deploying LiMEaide :(")

        return stdout

    def pull_sftp(self, remote_dir, local_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir ppath to output dir on local machine
        :param filename file to transfer
        """

        self.complete_percent = []
        if self.get_file_stat(remote_dir, filename):
            status = functools.partial(self.__transfer_status__, filename)
            self.SFTP.get(filename, local_dir + filename, callback=status)
            print('\n')

    def put_sftp(self, local_dir, remote_dir, filename):
        """Called when data needs to be pulled from remote system.

        dir params do not include the file name

        :param remote_dir path to file on remote host
        :param local_dir ppath to output dir on local machine
        :param filename file to transfer
        """
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

        except IOError:
            pass

        return file_exists

    def disconnect(self):
        """Call to end session and remove files from remote client."""
        cprint("cleaning up...", 'blue')
        self.exec_cmd('rm -rf ./.limeaide/', True)

        cprint("Removing LKM...standby", 'blue')
        self.exec_cmd('rmmod lime.ko', True)

        self.SFTP.close()

    def connect(self):
        """Call to set connection with remote client."""
        try:
            self.session = paramiko.SSHClient()
            self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.session.connect(
                self.client_.ip, username=self.client_.user,
                password=self.client_.pass_)

            self.SFTP = self.session.open_sftp()

        except paramiko.AuthenticationException as auth_except:
            print(colored("{}".format(auth_except), 'red'))
            sys.exit()
