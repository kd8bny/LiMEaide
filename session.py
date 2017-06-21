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

        self.complete_percent = []

    @staticmethod
    def _error_check(stdout):
        for line in stdout:
            if "error" in line.lower():
                return 1
        return 0

    def _transfer_status(self, filename, bytes_so_far, bytes_total):
        percent = int(100 * bytes_so_far / bytes_total)
        if percent % 10 == 0 and percent not in self.complete_percent:
            self.complete_percent.append(percent)
            print(
                colored("Transfer of %r is at %d/%d bytes (%.0f%%)\r"
                   % (filename, bytes_so_far, bytes_total, percent), 'cyan'), end='\r', flush=True)

    def connect(self):
        """Call to set connection with remote client."""
        try:
            self.session = paramiko.SSHClient()
            self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.session.connect(
                self.client_.ip, username=self.client_.user,
                password=self.client_.pass_)
        except paramiko.AuthenticationException as e:
            print(colored("{}".format(e), 'red'))
            sys.exit()

    def exec_cmd(self, cmd, requires_privlege):
        """Called to exec command on remote system.

        returns stdin, stdout, stderr.
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

        if not stderr or self._error_check(stdout):
            [print(line.strip('\n')) for line in stderr]
            sys.exit("Error deploying LiMEaide :(")

        return stdout

    def pull_sftp(self, rdir, ldir, filename):
        """Called when data needs to be pulled from remote system.

        (remote dir, local dir, file)
        """
        sftp = self.session.open_sftp()
        is_error = False

        if rdir:
            sftp.chdir(rdir)

        try:
            self.complete_percent = []
            sftp.stat(filename)
            status = functools.partial(self._transfer_status, filename)
            sftp.get(filename, ldir + filename, callback=status)

        except IOError as e:
            print(sftp.listdirs())
            print(rdir)
            print(filename)
            is_error = True

        finally:
            print('\n')
            sftp.close()
            return is_error

    def put_sftp(self, ldir, rdir, filename):
        """Called when data is to be sent to remote system.

        (local dir, remote dir, file)
        """
        sftp = self.session.open_sftp()
        if rdir:
            sftp.chdir(rdir)

        sftp.put(ldir + filename, filename)
        sftp.close()

    def clean(self):
        """Called to remove files from remote client."""
        cprint("cleaning up...", 'blue')
        self.exec_cmd('rm -rf /tmp/lime*', True)
        cprint("Removing LKM...standby", 'blue')
        self.exec_cmd('rmmod lime.ko', True)
