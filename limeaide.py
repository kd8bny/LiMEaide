#!/usr/bin/env python3

import sys
import os
import argparse
import getpass
import threading
import logging
import time
from datetime import datetime

from session import Session
from client import Client
from deploy_lime import LimeDeploy
from deploy_volatility import VolDeploy
from profiler import Profiler
from liMEaide_control import MasterControl

class Limeaide(object):
    """Deploy LiME LKM to remote host in order to scrape RAM."""

    _version = "1.2.3"

    def __init__(self):
        super(Limeaide, self).__init__()
        self.lime_dir = './tools/LiME/src/'
        self.tools_dir = './tools/'
        self.output_dir = './output/'
        self.profile_dir = './profiles/'
        self.args_case = ''
        self.log_dir = './logs'

    def check_tools(self):
        """Create dirs for profiles, LiME, logging, and output."""
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        if not os.path.isdir(self.profile_dir):
            os.mkdir(self.profile_dir)

        if not os.path.isdir(self.lime_dir):
            if not os.path.isdir(self.tools_dir):
                os.mkdir(self.tools_dir)
            sys.exit("Please download LiME and place in the ./tools/ dir")
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
        LOG_FILENAME = ''

    @staticmethod
    def get_args():
        """Take a look at those args."""
        parser = argparse.ArgumentParser(description='Utility designed to \
            automate GNU/Linux memory forensics')
        parser.add_argument("remote", help="remote host IP")
        parser.add_argument(
            "-P", "--no-profiler", action="store_true",
            help="Do NOT run profiler and compile new module/profile for \
            client")
        parser.add_argument(
            "-C", "--dont-compress", action="store_true", help="Do NOT compress\
            dump into Bzip2 format")
        parser.add_argument("-s", "--sudoer", help="use a sudo user instead \
            default: root")
        parser.add_argument(
            "-m", "--module", nargs=3, metavar=('distro', 'kernel', 'arch'),
            help="Provide the profile you know you want to use for the remote \
            client")
        parser.add_argument("-o", "--output", help="name the outputfile")
        parser.add_argument(
            "-c", "--case", help="Append case number to output dir")
        parser.add_argument("-B","--background", help="Enter wait time in minutes")
        parser.add_argument("--force-clean", action="store_true", help="Force \
            clean client after failed deployment")
        parser.add_argument("--version", action="store_true", help="Version \
            information")

        return parser.parse_args()

    def log_init(log_type, message):
        logging.b

    def get_client(self, args):
        """Return instantiated client."""
        client = Client()
        client.ip = args.remote
        if args.sudoer is not None:
            client.user = args.sudoer
            client.is_sudoer = True

        if args.output is not None:
            client.output = args.output

        if args.dont_compress:
            client.compress = not client.compress

        return client

    def lime_deploy_worker(self, session, profiler,schedule):
        """worker for threading lime deploy"""
        LimeDeploy(session,profiler,schedule)


    def main(self):
        """Start the interactive session for LiMEaide."""
        print(
            """\
            .---.                                                     _______
            |   |.--. __  __   ___         __.....__              .--.\  ___ `'.         __.....__
            |   ||__||  |/  `.'   `.   .-''         '.            |__| ' |--.\  \    .-''         '.
            |   |.--.|   .-.  .-.   ' /     .-''"'-.  `.          .--. | |    \  '  /     .-''"'-.  `.
            |   ||  ||  |  |  |  |  |/     /________\   \    __   |  | | |     |  '/     /________\   |
            |   ||  ||  |  |  |  |  ||                  | .:--.'. |  | | |     |  ||                  |
            |   ||  ||  |  |  |  |  |\    .-------------'/ |   \ ||  | | |     ' .'\    .-------------'
            |   ||  ||  |  |  |  |  | \    '-.____...---.`" __ | ||  | | |___.' /'  \    '-.____...---.
            |   ||__||__|  |__|  |__|  `.             .'  .'.''| ||__|/_______.'/    `.             .'
            '---'                        `''-...... -'   / /   | |_   \_______|/       `''-...... -'
                                                         \ \._,\ '/
                                                          `--'  `"
             by kd8bny v{0} \n""".format(self._version))
        print(
            "LiMEaide is licensed under GPL-3.0\n"
            "LiME is licensed under GPL-2.0\n")
        #set up logging file
        log_file = '{}-debug-limeaide.log'.format(datetime.strftime(datetime.today(),
             "%Y_%m_%dT%H_%M_%S_%f"))
        logging.basicConfig(filename=log_file,level=logging.DEBUG)

        self.check_tools()
        args = self.get_args()
        client = self.get_client(args)

        """used to hold sleep time for background jobs"""
        schedule = args.background

        if args.case is not None:
            self.args_case = 'case_%s' % (args.case)

        if args.version:
            sys.exit(_version)

        print("Attempting secure connection {0}@{1}".format(
            client.user, client.ip))
        client.pass_ = getpass.getpass()
        session = Session(client, args.background)
        profiler = Profiler()

        if not args.force_clean:
            profiler.main()
            client.output_dir = "{0}{1}{2}/".format(
                self.output_dir, self.args_case,
                datetime.strftime(datetime.today(), "%Y_%m_%dT%H_%M_%S_%f"))
            os.mkdir(client.output_dir)

            if not args.no_profiler:
                use_profile = input(
                    "Would you like to select a pre-generated profile [Y/n]")
                if use_profile.lower() == 'y':
                    profile = profiler.interactive_chooser()
                    if profile is None:
                        print("No profiles found... Will build new profile" +
                              "for remote client")
                    else:
                        client.profile = profile
            elif args.module is not None:
                profile = profiler.select_profile(
                    args.profile[0], args.profile[1], args.profile[2])
                if profile is None:
                    new_profile = input(
                        "No profiles found... Would you like to build a new" +
                        "profile for the remote client [Y/n]")
                    if new_profile.lower() == 'n':
                        sys.exit()
                else:
                    client.profile = profile
            getmem = LimeDeploy(session,profiler,schedule)
            getmem_name = "{0}-{1}-worker".format(client.ip,
                datetime.strftime(datetime.today(), "%Y_%m_%dT%H_%M_%S_%f"))
            getmem_thread = MasterControl(name=getmem_name,target=getmem.main, daemon=True)
            getmem_thread.start()
            #LimeDeploy(session, profiler).main()
            print(
               "Memory extraction is complete\n\n%s is in %s"
                % (client.output, client.output_dir))
            VolDeploy(session).main()
            print("Profile complete place in volatility/plugins/overlays/" +
                      "linux/ in order to use")
        else:
            session.clean()
            sys.exit("Clean attempt complete")


if __name__ == '__main__':
    #thread = threading.Thread(target=Limeaide().main(), name='limeAide-test')
    Limeaide().main()