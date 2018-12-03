import sys
from subprocess import Popen
from termcolor import colored, cprint
from lib.transfer import local
from lib.session.session import Session


class Local(Session):
    """Session will take care of all the backend communications."""

    def __init__(self, client, is_verbose=False):
        super(Local, self).__init__(client, is_verbose)

    def exec_cmd(self, cmd, requires_privlege, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param requires_privlege Does this command require elevated privileges
        :return stdout
        """
        cmd_args = cmd.split(' ')
        if self.client.user is not 'root' and requires_privlege:
            priv_esc = ['sudo', '-S', '-p']
            stdin.write(self.client_.pass_ + '\n')
            stdin.flush()

            #popen = Popen(['sudo', '-S', '-p', cmd_args])
        popen = Popen(cmd_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout = p.communicate(input=b'one\ntwo\nthree\nfour\nfive\nsix\n')[0]
        # print(grep_stdout.decode())

        self.logger.info("Command executed: {0}".format(cmd))

        self.__print__(stdout)

        if not stderr or self.__error_check__(stdout):
            for line in stderr:
                self.logger.error(line)
                print(line.strip('\n'))
            cprint("Error deploying LiMEaide :(", 'red')

            if disconnect_on_fail:
                self.disconnect()
                sys.exit()

        return stdout

    def connect(self):
        """Call to set connection with remote client."""

        self.transfer = local.Local()
        self.transfer.connect()
