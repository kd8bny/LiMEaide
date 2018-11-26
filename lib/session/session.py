import logging
from termcolor import colored, cprint


class Session:
    """Session will take care of all the backend communications."""

    def __init__(self, client, is_verbose):
        super(Session, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.client_ = client
        self.is_verbose = is_verbose

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
        pass

    def disconnect(self):
        """Call to end session and remove files from remote client."""
        pass

    def connect(self):
        """Call to set connection with remote client."""

        pass
