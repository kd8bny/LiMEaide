import time

class LimeDeploy(object):
    """Send LiME and retrieve the RAM dump from a remote client."""

    def __init__(self, session, profiler, schedule):
        super(LimeDeploy, self).__init__()
        self.remote_session = session
        self.client = session.client_
        self.profiler = profiler

        self.lime_dir = './tools/LiME/src/'
        self.lime_rdir = '/tmp/lime/'
        self.lime_src = ['disk.c', 'lime.h', 'main.c', 'Makefile', 'tcp.c']
        self.profiles_dir = './profiles/'
        self.schedule = int(schedule)

        self.new_profile = False

    def send_lime(self):
        """Send LiME to remote client. Uses percompiled module if supplied."""
        print("sending LiME to remote client")
        self.remote_session.exec_cmd('mkdir %s' % self.lime_rdir, False)
        if self.new_profile:
            for file in self.lime_src:
                self.remote_session.put_sftp(
                    self.lime_dir, self.lime_rdir, file)

            lsb_release = self.remote_session.exec_cmd('lsb_release -a', False)
            uname = self.remote_session.exec_cmd('uname -rm', False)
            self.client.profile = self.profiler.create_profile(
                lsb_release, uname)

            print("building kernel module")
            self.remote_session.exec_cmd(
                'cd {}; make'.format(self.lime_rdir), False)
        else:
            self.remote_session.put_sftp(
                self.profiles_dir, self.lime_rdir,
                self.client.profile["module"])
        print("done.")

        """Will install LiME and dump RAM."""
        print("Installing LKM and retrieving RAM")
        self.remote_session.exec_cmd("mv {0}lime.ko {0}{1}".format(
            self.lime_rdir, self.client.profile["module"]), False)
        self.remote_session.exec_cmd(
            "insmod {0}{1} 'path={2}{3} format=lime dio=0'".format(
                self.lime_rdir, self.client.profile["module"], self.lime_rdir,
                self.client.output), True)
        print("done.")
        print("Changing permissions")
        self.remote_session.exec_cmd(
            "chmod 755 {0}{1}".format(
                self.lime_rdir, self.client.output), True)
        print("done.")
        if self.client.compress:
            print("Creating Bzip2...compressing the following")
            self.remote_session.exec_cmd(
                'tar -jv --remove-files -f {0}{1}.bz2 -c {2}{3}'.format(
                    self.lime_rdir, self.client.output, self.lime_rdir,
                    self.client.output), True)
            self.client.output += ".bz2"
            print("done.")

    def get_lime_dump(self):
        print("Beam me up Scotty")
        self.remote_session.pull_sftp(
            self.lime_rdir, self.client.output_dir, self.client.output)
        if self.new_profile:
            self.remote_session.pull_sftp(
                self.lime_rdir, self.profiles_dir,
                self.client.profile['module'])

    def main(self):
        """Begin the process of transporting LiME and dumping the RAM."""
        if self.client.profile is None:
            self.new_profile = True
        self.send_lime()

        if self.schedule > 0:
            pause = self.schedule * 60
            time.sleep(pause)
        self.get_lime_dump()
