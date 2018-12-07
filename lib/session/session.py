import logging
from termcolor import cprint


class Session:
    """Session will take care of all the backend communications."""

    def __init__(self, config, client, is_verbose=False):
        super(Session, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.client = client
        self.is_verbose = is_verbose

    def __error_check__(self, stdout):
        """Check for standard errors from stdout"""
        for line in stdout:
            if "error" in line.lower():
                self.logger.error(line)
                return 1

        return 0

    def __print__(self, stdout):
        stdout = [line.strip() for line in stdout]
        for line in stdout:
            if line and line != self.client.pass_:
                self.logger.info(line)
                if self.is_verbose:
                    print(line)

    def disconnect(self):
        """Call to end session and remove files from remote client."""
        cprint("> Cleaning up...", 'blue')
        if self.transfer.file_stat(self.config.lime_rdir, ''):
            self.exec_cmd('rm -rf {0}'.format(
                self.config.lime_rdir), True, False)

        #TODO Check lsmod for lime before removing
        cprint("> Removing LKM...standby", 'blue')
        self.exec_cmd('rmmod lime.ko', True, False)

        self.transfer.close()

    def exec_cmd(self, cmd, priv=False, disconnect_on_fail=True):
        """Called to exec command on remote system.

        :param cmd The actual bash command to run on remote
        :param requires_privlege Does this command require elevated privileges
        :If command fails disconnect session
        :return stdout
        """
        pass

    def connect(self):
        """Call to set connection with remote client."""

        pass
