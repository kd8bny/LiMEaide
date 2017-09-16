#!/usr/bin/env python3

import sys
import os
import logging
import configparser
import argparse
import urllib.request
import zipfile
import getpass
import pickle
import shutil
from datetime import datetime
from termcolor import colored, cprint

from lib.session import Session
from lib.client import Client
from lib.deploy_lime import LimeDeploy
from lib.deploy_volatility import VolDeploy
from lib.profiler import Profiler


class Limeaide(object):
    """Deploy LiME LKM to remote host in order to scrape RAM."""

    __version__ = "1.3.1"
    __author__ = "kd8bny@gmail.com"

    def __init__(self):
        super(Limeaide, self).__init__()
        self.logger = None
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
        parser.add_argument("-v", "--verbose", action="store_true", help="Prod\
            uce verbose output from remote client")
        parser.add_argument("--force-clean", action="store_true", help="Force \
            clean client after failed deployment")

        return parser.parse_args()

    def check_tools(self):
        """Check for required tools and directories."""
        # Create config file
        if not os.path.isfile('.limeaide'):
            config = configparser.RawConfigParser()
            config.set('DEFAULT', 'volatility', '')
            config.set('DEFAULT', 'output', '')
            config.set('DEFAULT', 'compress', '')
            with open('.limeaide', 'w+') as config_file:
                config.write(config_file)

        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        if not os.path.isdir(self.profile_dir):
            os.mkdir(self.profile_dir)

        if not os.path.isdir(self.tools_dir):
                os.mkdir(self.tools_dir)

        if not os.path.isdir(self.lime_dir):
            lime_version = '1.7.8.1'
            self.logger.info("LiME not found. downloading")
            cprint("Downloading LiME", 'green')
            urllib.request.urlretrieve(
                "https://github.com/kd8bny/LiME/archive/v{}.zip".format(
                    lime_version), filename="./tools/lime_master.zip")
            zip_lime = zipfile.ZipFile("./tools/lime_master.zip", 'r')
            zip_lime.extractall('./tools/')
            zip_lime.close()
            shutil.move(
                './tools/LiME-{}'.format(lime_version), './tools/LiME/')

        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)

        if not os.path.isdir(self.scheduled_pickup_dir):
            os.mkdir(self.scheduled_pickup_dir)

        # Check to see if a volatility directory exists
        config = configparser.ConfigParser()
        config.read('.limeaide')
        config_vol_dir = config['DEFAULT']['volatility']
        if not config_vol_dir or not os.path.isdir(config_vol_dir):
            cprint(
                "Volatility directory missing. Current direcotry is:", 'red')
            cprint("{}".format(config_vol_dir), 'blue')
            cprint("Please provide a path to your Volatility directory." +
                   "\ne.g. '~/volatility/'" +
                   "\n[q] to never ask again: ", 'green')
            while True:
                path = input(":")
                if path == 'q':
                    path = 'None'
                    break
                elif os.path.isdir(path):
                    break
                else:
                    cprint(
                        "Entered directory does not exist. Please enter" +
                        "again", 'red')

            config.set('DEFAULT', 'volatility', path +
                       '/volatility/plugins/overlays/linux/')
            with open('.limeaide', 'w+') as configfile:
                config.write(configfile)

        self.volatility_profile_dir = config_vol_dir

    @staticmethod
    def get_client(args, config):
        """Return instantiated client.

        Config will provide global overrides.
        """
        client = Client()
        date = datetime.strftime(datetime.today(), "%Y_%m_%dT%H_%M_%S_%f")

        client.ip = args.remote
        client.jobname = "{0}-{1}-worker".format(client.ip, date)

        if args.user is not None:
            client.user = args.user
            client.is_sudoer = True

        if args.delay_pickup:
            client.delay_pickup = True

        if not config['DEFAULT']['output']:
            if args.output is not None:
                client.output = args.output

        if not config['DEFAULT']['compress']:
            if args.dont_compress:
                client.compress = not client.compress

        cprint("> Establishing secure connection {0}@{1}".format(
            client.user, client.ip), 'blue')
        client.pass_ = getpass.getpass()

        return client

    def save_job(self, client, jobname):
        """Save client with pickle.

        Format will be <date>-worker.dat
        """
        pickle.dump(client, open(("{0}{1}.dat".format(
            self.scheduled_pickup_dir, jobname)), 'wb'))

    def finish_saved_job(self, jobname):
        """Restore client with pickle. Transfer dump."""
        restored_client = pickle.load(open(jobname, 'rb'))
        cprint("Client restored!", 'green')
        cprint("Retrieving RAM dump {}".format(restored_client.output), 'blue')

        if not os.path.isdir(restored_client.output_dir):
            os.mkdir(restored_client.output_dir)

        saved_session = Session(restored_client)
        delayed_profiler = Profiler()
        LimeDeploy(saved_session, delayed_profiler).transfer_dump()
        VolDeploy(saved_session).main(self.volatility_profile_dir)
        cprint(
            "Job {} pickup has been completed!".format(
                restored_client.output), 'green')
        saved_session.disconnect()
        os.remove(jobname)

    def main(self):
        """Start the interactive session for LiMEaide."""
        cprint(
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
             by kd8bny {0}\n""".format(
                self.__version__), 'green', attrs=['bold'])
        print(
            "LiMEaide is licensed under GPL-3.0\n"
            "LiME is licensed under GPL-2.0\n")

        date = datetime.strftime(datetime.today(), "%Y_%m_%dT%H_%M_%S_%f")
        logging.basicConfig(
            level=logging.INFO, filename='{0}{1}.log'.format(
                self.log_dir, date))
        self.logger = logging.getLogger()

        args = self.get_args()
        self.check_tools()
        config = configparser.ConfigParser()
        config.read('.limeaide')
        profiler = Profiler()
        profiler.load_profiles()
        client = self.get_client(args, config)

        if args.pickup:
            self.finish_saved_job(args.pickup)
            sys.exit("goodbye")

        if args.case is not None:
            self.args_case = 'case_%s' % (args.case)

        # Start session
        session = Session(client, args.verbose)
        session.connect()
        client.output_dir = "{0}{1}{2}/".format(
            self.output_dir, self.args_case, date)
        os.mkdir(client.output_dir)

        if args.force_clean:
            session.disconnect()
            sys.exit("Clean attempt complete")

        if args.profile is not None:
            profile = profiler.select_profile(
                args.profile[0], args.profile[1], args.profile[2])
            if profile is None:
                new_profile = input(colored(
                    "No profiles found... Would you like to build a new" +
                    "profile for the remote client [Y/n]", 'red'))
                if new_profile.lower() == 'n':
                    sys.exit()
            else:
                client.profile = profile
                cprint("Profile found!", 'green')

        elif not args.no_profiler:
            use_profile = input(colored(
                "Would you like to select a pre-generated profile " +
                "[Y/n]", 'green'))
            if use_profile.lower() == 'y':
                profile = profiler.interactive_chooser()
                if profile is None:
                    cprint("No profiles found... Will build new profile" +
                           "for remote client", 'red')
                else:
                    client.profile = profile

        LimeDeploy(session, profiler).main()

        if args.delay_pickup:
            self.save_job(client, client.jobname)
            cprint("RAM dump retrieval is postponed 0_0\nLATERZ!", 'blue')
        else:
            # Now that's taken care of, lets do work
            VolDeploy(session).main(self.volatility_profile_dir)
            session.disconnect()
        logging.shutdown()


if __name__ == '__main__':
    Limeaide().main()
