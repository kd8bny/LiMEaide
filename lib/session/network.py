import sys
import paramiko
from termcolor import colored, cprint
from lib.transfer import network
from lib.session.session import Session


class Network(Session):
    """Session will take care of all the backend communications."""

    def __init__(self, config, client, is_verbose=False):
        Session.__init__(self, config, client, is_verbose)
        self.paramiko_session = None
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
        if self.client.user is not 'root' and requires_privlege:
            cmd = "sudo -S -p ' ' {0}".format(cmd)
            self.logger.info("Command executed: {0}".format(cmd))
            stdin, stdout, stderr = self.paramiko_session.exec_command(
                cmd, get_pty=True)
            stdin.write(self.client.pass_ + '\n')
            stdin.flush()
        else:
            self.logger.info("Command executed: {0}".format(cmd))
            stdin, stdout, stderr = self.paramiko_session.exec_command(
                cmd, get_pty=True)
        output = stdout.readlines()

        self.__print__(output)

        if not stderr or self.__error_check__(stdout):
            for line in stderr:
                self.logger.error(line)
                print(line.strip('\n'))
            cprint("Error deploying LiMEaide :(", 'red')

            if disconnect_on_fail:
                self.disconnect()
                sys.exit()

        return output

    def connect(self):
        """Call to set connection with remote client."""

        try:
            self.paramiko_session = paramiko.SSHClient()
            self.paramiko_session.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.paramiko_session.connect(
                self.client.ip, username=self.client.user,
                password=self.client.pass_)

        except (paramiko.AuthenticationException,
                paramiko.ssh_exception.NoValidConnectionsError) as e:
            self.logger.error(e)
            sys.exit(colored("> {}".format(e), 'red'))

        self.transfer = network.Network(
            self.paramiko_session, None,
            self.client.ip, self.client.port)
        self.transfer.connect()
