from termcolor import colored, cprint


class LimeDeploy(object):
    """Send LiME and retrieve the RAM dump from a remote client."""

    def __init__(self, session, profiler):
        super(LimeDeploy, self).__init__()
        self.remote_session = session
        self.client = session.client_
        self.profiler = profiler

        self.lime_dir = './tools/LiME/src/'
        self.lime_rdir = '/tmp/lime/'
        self.lime_src = ['disk.c', 'lime.h', 'main.c', 'Makefile']
        self.profiles_dir = './profiles/'

        self.new_profile = False

    def send_lime(self):
        """Send LiME to remote client. Uses percompiled module if supplied."""
        cprint("sending LiME to remote client", 'blue')
        self.remote_session.exec_cmd('mkdir %s' % self.lime_rdir, False)

        # Generate information to create a new profile
        if self.new_profile:
            for file in self.lime_src:
                self.remote_session.put_sftp(
                    self.lime_dir, self.lime_rdir, file)

            lsb_release = self.remote_session.exec_cmd('lsb_release -a', False)
            uname = self.remote_session.exec_cmd('uname -rm', False)
            self.client.profile = self.profiler.create_profile(
                lsb_release, uname)

            cprint("building kernel module", 'blue')
            self.remote_session.exec_cmd(
                'cd {}; make'.format(self.lime_rdir), False)
            self.remote_session.exec_cmd("mv {0}lime.ko {0}{1}".format(
                self.lime_rdir, self.client.profile["module"]), False)
        # Use an old profile
        else:
            self.remote_session.put_sftp(
                self.profiles_dir, self.lime_rdir,
                self.client.profile["module"])

    def get_lime_dump(self):
        """Will install LiME and dump RAM."""
        cprint("Installing LKM and retrieving RAM", 'blue')
        self.remote_session.exec_cmd(
            "insmod {0}{1} 'path={2}{3} format=lime dio=0'".format(
                self.lime_rdir, self.client.profile["module"], self.lime_rdir,
                self.client.output), True)

        cprint("Changing permissions", 'blue')
        self.remote_session.exec_cmd(
            "chmod 755 {0}{1}".format(
                self.lime_rdir, self.client.output), True)

        if self.client.compress:
            cprint("Creating Bzip2...compressing the RAM dump", 'blue')
            self.remote_session.exec_cmd(
                'tar -jv --remove-files -f {0}{1}.bz2 -c {2}{3}'.format(
                    self.lime_rdir, self.client.output, self.lime_rdir,
                    self.client.output), True)

    def transfer_dump(self):
        """Retrieve files from remote client."""
        cprint("Beam me up Scotty", 'blue')
        self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, self.client.output)

        if self.new_profile:
            self.remote_session.pull_sftp(
                self.lime_rdir, self.profiles_dir,
                self.client.profile['module'])
        cprint("Memory extraction is complete\n\n{0} is in {1}".format(
            self.client.output, self.client.output_dir), 'green')

    def main(self):
        """Begin the process of transporting LiME and dumping the RAM."""
        if self.client.profile is None:
            self.new_profile = True

        self.send_lime()
        self.get_lime_dump()

        if not self.client.delay_pickup:
            self.transfer_dump()
