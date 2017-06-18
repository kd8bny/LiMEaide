#!/usr/bin/env python3

import sys
import os
import configparser
import argparse
import getpass
import logging
import pickle
from datetime import datetime

from session import Session
from client import Client
from deploy_lime import LimeDeploy
from deploy_volatility import VolDeploy
from profiler import Profiler


class Limeaide(object):
    """Deploy LiME LKM to remote host in order to scrape RAM."""

    _version = ":prototype-delayedJobs"

    def __init__(self):
        super(Limeaide, self).__init__()
        self.volatility_profile_dir = None
        self.lime_dir = './tools/LiME/src/'
        self.tools_dir = './tools/'
        self.output_dir = './output/'
        self.profile_dir = './profiles/'
        self.log_dir = './logs/'
        self.scheduled_pickup_dir = './scheduled_jobs/'

        self.args_case = ''

    @staticmethod
    def get_args():
        """Take a look at those args."""
        parser = argparse.ArgumentParser(description='Utility designed to \
            automate GNU/Linux memory forensics')
        parser.add_argument("remote", help="remote host IP")
        parser.add_argument("-u", "--user", help="use a sudo user instead \
            default: root")
        parser.add_argument(
            "-N", "--no-profiler", action="store_true",
            help="Do NOT run profiler and force compile new module/profile for \
            client")
        parser.add_argument(
            "-p", "--profile", nargs=3, metavar=('disto', 'kver', 'arch'),
            help="Skip the profiler by providing the distribution, kernel\
            version, and architecture of the remote client.")
        parser.add_argument(
            "-C", "--dont-compress", action="store_true", help="Do NOT compress\
            dump into Bzip2 format")
        parser.add_argument("-o", "--output", help="name the output file")
        parser.add_argument("-c", "--case", help="Append case number to output\
            dir")
        parser.add_argument("--delay-pickup", action="store_true", help="Used \
            to store job for future pickup")
        parser.add_argument("-P", "--pickup", help="Enter stored job file")
        parser.add_argument("--force-clean", action="store_true", help="Force \
            clean client after failed deployment")
        parser.add_argument("--version", action="store_true", help="Version \
            information")

        return parser.parse_args()

    def check_tools(self, config):
        """Check for required tools and directories."""
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

        if not os.path.isdir(self.scheduled_pickup_dir):
            os.mkdir(self.scheduled_pickup_dir)

        # Check to see if a volatility directory exists
        config_vol_dir = config['DEFAULT']['volatility']
        if config_vol_dir is '' or not os.path.isdir(config_vol_dir):
            path = input(
                "Volatility directory missing. Please provide a path to " +
                "your Volatility directory. \n[q] to never ask again: ")
            if path == 'q':
                path = 'None'

            config.set('DEFAULT', 'volatility', path +
                       '/volatility/plugins/linux/')
            with open('.limeaide', 'w') as configfile:
                config.write(configfile)

        self.volatility_profile_dir = config_vol_dir

    @staticmethod
    def get_client(args, config):
        """Return instantiated client.
        Config will provide global overrides.
        """
        client = Client()
        client.ip = args.remote
        if args.user is not None:
            client.user = args.user
            client.is_sudoer = True

        if args.delay_pickup:
            client.delay_pickup = True

        if config['DEFAULT']['output'] is not '':
            if args.output is not None:
                client.output = args.output

        if config['DEFAULT']['compress'] is not '':
            if args.dont_compress:
                client.compress = not client.compress

        return client

    def save_job(self, client, jobname):
        pickle.dump(client, open(("{0}{1}.dat".format(
            self.scheduled_pickup_dir, jobname)), 'wb'))

    def get_saved_job(self, stored_client):
        restored_client = pickle.load(open(stored_client, 'rb'))
        print("Client restored!")

        return restored_client

    def finish_saved_job(self, client):
        print("Retrieving RAM dump {}".format(client.output))
        if not os.path.isdir(client.output_dir):
            os.mkdir(client.output_dir)
        savedSession = Session(client)
        delayedProfiler = Profiler()
        LimeDeploy(savedSession, delayedProfiler).transfer_dump()
        print("Job {} pickup has been completed!".format(client.output))
        savedSession.clean()

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

        date = datetime.strftime(datetime.today(), "%Y_%m_%dT%H_%M_%S_%f")

        args = self.get_args()
        config = configparser.ConfigParser()
        config.read('.limeaide')
        self.check_tools(config)
        client = self.get_client(args, config)

        # Set up logging files
        info_log_file = '{0}{1}-info-limeaide.log'.format(self.log_dir, date)
        debug_log_file = '{0}{1}-debug-limeaide.log'.format(self.log_dir, date)
        logging.basicConfig(filename=info_log_file, level=logging.INFO)
        logging.basicConfig(filename=debug_log_file, level=logging.DEBUG)

        if args.pickup:
            job = self.get_saved_job(args.pickup)
            self.finish_saved_job(job)
            sys.exit("goodbye")

        if args.case is not None:
            self.args_case = 'case_%s' % (args.case)

        if args.version:
            sys.exit(self._version)

        print("Attempting secure connection {0}@{1}".format(
            client.user, client.ip))
        client.pass_ = getpass.getpass()

        client.jobname = "{0}-{1}-worker".format(client.ip, date)

        session = Session(client)
        profiler = Profiler()

        if not args.force_clean:
            profiler.main()
            client.output_dir = "{0}{1}{2}/".format(
                self.output_dir, self.args_case, date)
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

            LimeDeploy(session, profiler).main()

            VolDeploy(session).main(self.volatility_profile_dir)
            print("Profile complete place in volatility/plugins/overlays/" +
                  "linux/ in order to use")

            if args.delay_pickup:
                self.save_job(client, client.jobname)
                print("RAM dump retrieval is postponed 0_0\nLATERZ!")
            else:
                session.clean()

        else:
            session.clean()
            sys.exit("Clean attempt complete")


if __name__ == '__main__':
    Limeaide().main()
