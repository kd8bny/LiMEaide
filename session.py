#/bin/python

import paramiko, sys


class Session(object):
    """Session will take care of all the backend communications"""
    def __init__(self, client):
        super(Session, self).__init__()
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

        [print(line.strip('\n')) for line in stdout]
        if not stderr:
            print(len(stderr))
            [print(line.strip('\n')) for line in stderr]
            sys.exit()


        return stderr, stdout

    def pull_sftp(self, rdir, ldir, file):
        """Called when data needs to be pulled from remote system (remote dir, local dir, file)"""
        sftp = self.session.open_sftp()
        if rdir:
            sftp.chdir(rdir)
        sftp.get(file, ldir + file)
        sftp.close

    def put_sftp(self, ldir, rdir, file):
        """Called when data is to be sent to remote system (local dir, remote dir, file)"""
        sftp = self.session.open_sftp()
        if rdir:
            sftp.chdir(rdir)
        sftp.put(ldir + file, file)
        sftp.close
