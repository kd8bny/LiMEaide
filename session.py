#/bin/python

import paramiko, logging


class Session(object):
    """Session will take care of all the backend communications"""
    def __init__(self, client):
        super(Session, self).__init__()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.client = client
        self.session = paramiko.SSHClient()
        self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.session.connect(client.ip, username=client.user, password=client.pass_)

    def exec_cmd(self, cmd, requires_privlege):
        """Called when one wants to exec command on remote system returns result in stdin, stdout, stderr"""
        stdout, stderr = None, None
        if self.client.is_sudoer and requires_privlege:
            stdin, stdout, stderr = self.session.exec_command('sudo -S -p " " %s' % cmd)
            stdin.write(self.client.pass_ + "\n")
            stdin.flush()
        else:
            stdin, stdout, stderr = self.session.exec_command(cmd)

        if stdout != None:
            for line in stdout:
                self.logger.info(line.strip('\n'))
        if stderr != None:
            for line in stderr:
                self.logger.error(line.strip('\n'))

    def pull_sftp(self, dir, file):
        """Called when data needs to be pulled from remote system"""
        sftp = self.session.open_sftp()
        sftp.get(dir + file, file)
        sftp.close()

    def put_sftp(self, dir, file):
        """Called when data is to be sent to remote system"""
        sftp = self.session.open_sftp()
        sftp.put(dir + file, file)
        sftp.close()
