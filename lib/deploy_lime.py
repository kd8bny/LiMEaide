import logging
from termcolor import cprint
import hashlib


class LimeDeploy(object):
    """Send LiME and retrieve the RAM dump from a remote client."""

    def __init__(self, config, session, profiler):
        super(LimeDeploy, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session
        self.client = session.client
        self.profiler = profiler

        self.new_profile = False

    def send_lime(self):
        """Send LiME to remote client. Uses pre-compiled module if supplied."""
        cprint("> Sending LiME src to remote client", 'blue')
        lime_src = ['main.c', 'disk.c', 'tcp.c', 'hash.c', 'lime.h',
                    'Makefile']

        self.session.exec_cmd(
            'mkdir -p {}'.format(self.config.lime_rdir), False)

        # Generate information to create a new profile
        if self.new_profile:
            for file in lime_src:
                self.session.transfer.put(
                    self.config.lime_dir, self.config.lime_rdir, file)

            self.client.profile = self.profiler.create_profile(
                self.session)
            print(self.client.profile["module"])

            cprint("> Building loadable kernel module", 'blue')
            self.session.exec_cmd(
                'cd {}; make debug'.format(self.config.lime_rdir), False)
            self.session.exec_cmd("mv {0}lime-{1}.ko {0}{2}".format(
                self.config.lime_rdir, self.client.profile["kver"],
                self.client.profile["module"]), False)

            self.logger.info(
                "new profile created {0}".format(
                    self.client.profile["module"]))

        # Use an old profile
        else:
            self.session.transfer.put(
                self.profiles_dir, self.config.lime_rdir,
                self.client.profile["module"])

            self.logger.info(
                "Old profile used {0}".format(self.client.profile["module"]))
        cprint("> Detected {0} {1} {2}".format(
            self.client.profile["distro"], self.client.profile["kver"],
            self.client.profile["arch"]), 'blue')

    def get_lime_dump(self):
        """Will install LiME and dump RAM."""
        cprint("> Installing LKM and retrieving RAM", 'blue')

        # Build the correct instructions
        insmod_path = ""
        #if self.client.transfer == 'raw':
        #    insmod_path = "path=tcp:{}".format(self.client.port)
        #else:
        insmod_path = "path={0}{1}".format(
                self.config.lime_rdir, self.client.output)
        insmod_format = "format={}".format(self.client.format)
        insmod_digest = '' #"digest={}".format(self.client.digest)

        cprint(">> {}".format(insmod_path), 'blue')
        cprint(">> {}".format(insmod_format), 'blue')
        cprint(">> {}".format(insmod_digest), 'blue')

        insmod_cmd = "insmod {0}{1} '{2} {3} {4}'".format(
            self.config.lime_rdir, self.client.profile["module"],
            insmod_path, insmod_format, insmod_digest)

        self.session.exec_cmd(insmod_cmd, True)

        self.logger.info("LiME installed")

        #if self.client.transfer != 'raw':
        cprint("> Changing permissions", 'blue')
        self.session.exec_cmd(
            "chmod 755 {0}{1}".format(
                self.config.lime_rdir, self.client.output), True)

        # if self.client.compress:
        #     cprint(
        #         "> Compressing image to Bzip2...This will take awhile", 'blue')
        #     self.session.exec_cmd(
        #         'tar -jv --remove-files -f {0}{1}.bz2 -c {2}{3}'.format(
        #             self.lime_rdir, self.client.output, self.lime_rdir,
        #             self.client.output), True)

    def transfer_dump(self):
        """Retrieve files from remote client."""
        cprint("> Beam me up Scotty", 'blue')
        remote_file = self.client.output
        remote_file_hash = "{}.{}".format(
            self.client.output, self.client.digest)
        #if self.client.transfer == 'raw':
        #     self.session.transfer.pull(
        #         None, self.client.output_dir, remote_file)
        #     self.session.transfer.pull(
        #         None, self.client.output_dir, remote_file_hash)
        # else:
        #if self.client.compress:
        #    remote_file += '.bz2'
        self.session.transfer.pull(
            self.config.lime_rdir, self.client.output_dir, remote_file)
        self.session.transfer.pull(
            self.config.lime_rdir, self.client.output_dir, remote_file_hash)

        if self.new_profile:
            self.session.transfer.pull(
                self.lime_rdir, self.profiles_dir,
                self.client.profile['module'])

        cprint("> Memory extraction is complete", 'blue')
        cprint("{0} is in {1}".format(
            self.client.output, self.client.output_dir), 'cyan')

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
