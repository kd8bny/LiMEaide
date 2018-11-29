import sys
from subprocess import Popen
from termcolor import colored, cprint
from lib.transfer import local
from lib.session.session import Session


class Local(Session):
    """Session will take care of all the backend communications."""

    def __init__(self, client, is_verbose=False):
        super(Local, self).__init__()
        self.is_verbose = is_verbose

    def exec_cmd(self, cmd, requires_privlege, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param requires_privlege Does this command require elevated privileges
        :return stdout
        """
        if self.client_.user is not 'root' and requires_privlege:
            pf = Popen(['sudo', '-S', '-p', cmd])

            # self.logger.info("Command executed: {0}".format(cmd))
            stdin.write(self.client_.pass_ + '\n')
            stdin.flush()
        else:
            #self.logger.info("Command executed: {0}".format(cmd))
            pf = Popen(cmd)

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

        if self.client_.ip == 'local':
            self.transfer = local.Local()

        else:
            try:
                self.paramiko_session = paramiko.SSHClient()
                self.paramiko_session.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                self.paramiko_session.connect(
                    self.client_.ip, username=self.client_.user,
                    password=self.client_.pass_)

            except (paramiko.AuthenticationException,
                    paramiko.ssh_exception.NoValidConnectionsError) as e:
                self.logger.error(e)
                sys.exit(colored("> {}".format(e), 'red'))

            self.transfer = network.Network(
                self.paramiko_session, self.client_.transfer,
                self.client_.ip, self.client_.port)

        self.transfer.connect()
