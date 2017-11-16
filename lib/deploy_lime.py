import logging
from termcolor import cprint
import hashlib


class LimeDeploy(object):
    """Send LiME and retrieve the RAM dump from a remote client."""

    def __init__(self, session, profiler):
        super(LimeDeploy, self).__init__()
        self.logger = logging.getLogger()
        self.remote_session = session
        self.client = session.client_
        self.profiler = profiler

        self.lime_dir = './tools/LiME/src/'
        self.lime_rdir = './.limeaide/'
        self.profiles_dir = './profiles/'

        self.new_profile = False

    def send_lime(self):
        """Send LiME to remote client. Uses pre-compiled module if supplied."""
        cprint("> Sending LiME src to remote client", 'blue')
        lime_src = ['main.c', 'disk.c', 'tcp.c', 'hash.c', 'lime.h',
                    'Makefile']
        self.remote_session.exec_cmd('mkdir %s' % self.lime_rdir, False)

        # Generate information to create a new profile
        if self.new_profile:
            for file in lime_src:
                self.remote_session.put_sftp(
                    self.lime_dir, self.lime_rdir, file)

            self.client.profile = self.profiler.create_profile(
                self.remote_session)

            cprint("> Building loadable kernel module", 'blue')
            self.remote_session.exec_cmd(
                'cd {}; make'.format(self.lime_rdir), False)
            self.remote_session.exec_cmd("mv {0}lime.ko {0}{1}".format(
                self.lime_rdir, self.client.profile["module"]), False)

            self.logger.info(
                "new profile created {0}".format(
                    self.client.profile["module"]))
        # Use an old profile
        else:
            self.remote_session.put_sftp(
                self.profiles_dir, self.lime_rdir,
                self.client.profile["module"])

            self.logger.info(
                "Old profile used {0}".format(self.client.profile["module"]))
        cprint("> Detected {0} {1} {2}".format(
            self.client.profile["distro"], self.client.profile["kver"],
            self.client.profile["arch"]), 'blue')

    def get_lime_dump(self):
        """Will install LiME and dump RAM."""
        cprint("> Installing LKM and retrieving RAM", 'blue')
        self.remote_session.exec_cmd(
            "insmod {0}{1} 'path={2}{3} format=lime digest=sha1'".format(
                self.lime_rdir, self.client.profile["module"], self.lime_rdir,
                self.client.output), True)

        cprint("> Changing permissions", 'blue')
        self.remote_session.exec_cmd(
            "chmod 755 {0}{1}".format(
                self.lime_rdir, self.client.output), True)

        self.logger.info("LiME installed")

        if self.client.compress:
            cprint(
                "> Compressing image to Bzip2...This will take awhile", 'blue')
            self.remote_session.exec_cmd(
                'tar -jv --remove-files -f {0}{1}.bz2 -c {2}{3}'.format(
                    self.lime_rdir, self.client.output, self.lime_rdir,
                    self.client.output), True)

    def transfer_dump(self):
        """Retrieve files from remote client."""
        cprint("> Beam me up Scotty", 'blue')
        remote_file = self.client.output
        remote_file_hash = self.client.output + ".sha1"
        if self.client.compress:
            remote_file += '.bz2'

        self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, remote_file)
        self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, remote_file_hash)

        if self.new_profile:
            self.remote_session.pull_sftp(
                self.lime_rdir, self.profiles_dir,
                self.client.profile['module'])

        cprint("> Memory extraction is complete\n\n{0} is in {1}".format(
            self.client.output, self.client.output_dir), 'green')

    def check_integrity(self):
        BUFF_SIZE = 65536
        digest = hashlib.sha1()

        cprint("> Computing message digest of image", 'blue')
        with open(self.client.output_dir + self.client.output, 'rb') as f:
            while True:
                data = f.read(BUFF_SIZE)
                if not data:
                    break
                digest.update(data)
        sha1 = digest.hexdigest()

        with open(self.client.output_dir +
                  self.client.output + '.sha1', 'r') as f:
            remote_sha1 = f.read()

        if sha1 == remote_sha1:
            cprint("> Digest complete (sha1) {}".format(sha1), 'green')
        else:
            cprint("> DIGEST MISMATCH (sha1) \nlocal  {0} \nremote {1}".format(
                sha1, remote_sha1), 'red')

    def main(self):
        """Begin the process of transporting LiME and dumping the RAM."""
        if self.client.profile is None:
            self.new_profile = True

        self.send_lime()
        self.get_lime_dump()

        if not self.client.delay_pickup:
            self.transfer_dump()

            if not self.client.compress:
                self.check_integrity()
