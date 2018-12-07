import sys
from subprocess import Popen, PIPE
from termcolor import colored, cprint
from lib.transfer import local
from lib.session.session import Session


class Local(Session):
    """Session will take care of all the backend communications."""

    def __init__(self, config, client, is_verbose=False):
        super(Local, self).__init__(config, client, is_verbose)

    def exec_cmd(self, cmd, priv=False, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param priv Does this command require elevated privileges
        :If command fails disconnect session
        :return stdout
        """
        popen = None
        stdout, stderr = None, None
        if self.client.user is not 'root' and priv:
            cmd = "sudo -S -p ' ' {0}".format(cmd)
            popen = Popen(
                cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = popen.communicate(
                bytes(self.client.pass_, 'utf-8'))
        else:
            popen = Popen(
                cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = popen.communicate()

        output = stdout.decode('utf-8')
        output = output.split("\n")

        self.__print__(output)
        self.logger.info("Command executed: {0}".format(cmd))

        error = stderr.decode('utf-8')
        error = error.split("\n")

        if not error or self.__error_check__(output):
            for line in error:
                self.logger.error(line)
                print(line.strip('\n'))
            cprint("Error deploying LiMEaide :(", 'red')

            if disconnect_on_fail:
                self.disconnect()
                sys.exit()

        return output

    def connect(self):
        """Call to set connection with remote client."""

        self.transfer = local.Local()
        self.transfer.connect()
