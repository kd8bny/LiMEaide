import sys
import logging
import paramiko
from termcolor import colored, cprint
from lib.transfer import sftp


class Session:
    """Session will take care of all the backend communications."""

    def __init__(self, client, is_verbose=False):
        super(Session, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.client_ = client
        self.is_verbose = is_verbose
        self.remote_session = None
        self.transfer = None

    def __error_check__(self, stdout):
        """Check for standard errors from stdout"""
        for line in stdout:
            if "error" in line.lower():
                self.logger.error(line)
                return 1

        return 0

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
            stdin, stdout, stderr = self.remote_session.exec_command(
                cmd, get_pty=True)
            stdin.write(self.client_.pass_ + '\n')
            stdin.flush()
        else:
            self.logger.info("Command executed: {0}".format(cmd))
            stdin, stdout, stderr = self.remote_session.exec_command(
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

    def disconnect(self):
        """Call to end session and remove files from remote client."""
        cprint("> Cleaning up...", 'blue')
        self.exec_cmd('rm -rf ./.limeaide/', True, False)

        cprint("> Removing LKM...standby", 'blue')
        self.exec_cmd('rmmod lime.ko', True, False)

        self.transfer.close()
        cprint("> Done", 'green')

    def connect(self):
        """Call to set connection with remote client."""
        try:
            self.remote_session = paramiko.SSHClient()
            self.remote_session.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.remote_session.connect(
                self.client_.ip, username=self.client_.user,
                password=self.client_.pass_)

            if self.client_.transfer == 'raw':
                # self.transfer = transfer.Raw()
                # TODO we still need SFTP for profiles
                pass
            elif self.client_.transfer == 'local':
                # self.transfer = transfer.Local()
                pass
            else:
                self.transfer = sftp.SFTP(self.remote_session)

            self.transfer.connect()

        except (paramiko.AuthenticationException,
                paramiko.ssh_exception.NoValidConnectionsError) as e:
            print(colored("> {}".format(e), 'red'))
            self.logger.error(e)
            sys.exit()
