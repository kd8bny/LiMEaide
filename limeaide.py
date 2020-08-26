#!/usr/bin/env python3
# encoding: utf-8

# LiMEaide
# Copyright (c) 2011-2018 Daryl Bennett

# Author:
# Daryl Bennett - kd8bny@gmail.com

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import argparse
import getpass
import logging
import sys

from termcolor import colored, cprint

from lib.config import Config
from lib.session import local, network
from lib.client import Client
from lib.deploy_lime import LimeDeploy
from lib.deploy_volatility import VolDeploy
from lib.profiler import Profiler


class Limeaide:
    """Deploy LiME LKM to remote host in order to scrape RAM."""

    __version__ = "2.0.1"
    __author__ = "kd8bny@gmail.com"

    def __init__(self):
        super(Limeaide, self).__init__()
        self.logger = None

    @staticmethod
    def __get_args__():
        """Take a look at those args."""

        parser = argparse.ArgumentParser(description='Utility designed to \
            automate GNU/Linux memory forensics')
        parser.add_argument("remote", help="IP address of remote host. Use \
            'local' in place of IP to run locally")

        # LiMEaide Options
        parser.add_argument("-u", "--user", help="use a sudo user instead \
            default: root")
        parser.add_argument("-k", "--key", help="use a SSH Key to connect")
        parser.add_argument(
            "-s", "--socket", help="Use a TCP socket instead of a SFTP session \
            to transfer data. Does not write the memory image to disk, but \
            will transfer other needed files")
        parser.add_argument("-c", "--case", help="Append case title or number \
            to the output directory")
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Produce verbose \
            output from remote client")
        parser.add_argument("--force-clean", action="store_true", help="Force \
            clean client after failed deployment")

        # LiME Options
        parser.add_argument("-o", "--output", help="Name the output file")
        parser.add_argument("-f", "--format", help="Change the format")
        parser.add_argument("-d", "--digest", help="Use a different digest\
             algorithm. Default is 'sha1', use 'None' to disable")
        parser.add_argument(
            "-z", "--zlib", action="store_true", help="Compress the \
            memory image during imaging using LiME zlib. This will speed \
            up imaging and transfer by compressng the image during paging. \
            See README for decompression")

        profiler_group = parser.add_mutually_exclusive_group()
        profiler_group.add_argument(
            "-N", "--no-profiler", action="store_true",
            help="Do NOT run profiler and force compile new module/profile for \
            client")
        profiler_group.add_argument(
            "-p", "--profile", nargs=3, metavar=('disto', 'kver', 'arch'),
            help="Skip the profiler by providing the distribution, kernel\
            version, and architecture of the remote client.")

        return parser.parse_args()

    @staticmethod
    def __get_client__(args, config):
        """Return instantiated client.

        Args will override global config defaults.
        """

        client = Client()
        client.ip = args.remote

        # Check args for remote/local issues
        if client.ip == 'local':
            if args.socket:
                sys.exit(colored("Can not use socket on local machine", 'red'))

        if args.socket:
            client.port = int(args.socket)

        if args.case:
            client.job_name = args.case
        else:
            client.job_name = "{0}_{1}".format(
                client.ip, config.date)

        if args.user:
            client.user = args.user
        else:
            client.user = 'root'

        if args.format:
            client.format = args.format
        else:
            client.format = config.format

        if args.digest:
            if args.digest == 'None':
                client.digest = ''
            else:
                client.digest = args.digest
        else:
            client.digest = config.digest

        if args.output:
            client.output = args.output
        else:
            client.output = config.output

        if args.zlib:
            client.zlib = args.zlib

        client.output_dir = "{0}{1}/".format(
            config.output_dir, client.job_name)

        cprint("> Establishing secure connection {0}@{1}".format(
            client.user, client.ip), 'blue')
        if args.key:
            client.key = args.key
            cprint("> Please enter key pass phrase", 'blue')

        client.pass_ = getpass.getpass()

        return client

    def display_header(self):
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

    def main(self):
        """Start the interactive session for LiMEaide."""

        self.display_header()
        config = Config()
        config.configure()
        profiler = Profiler(config)
        profiler.load_profiles()

        args = self.__get_args__()
        client = self.__get_client__(args, config)

        # Start session
        session = None
        if client.ip == 'local':
            session = local.Local(config, client, args.verbose)
        else:
            session = network.Network(config, client, args.verbose)

        session.connect()

        if args.force_clean:
            session.disconnect()
            sys.exit(colored("> Clean attempt complete", 'green'))

        if args.profile:
            profile = profiler.select_profile(
                args.profile[0], args.profile[1], args.profile[2])
            if profile is None:
                new_profile = input(colored(
                    "No profiles found... Would you like to build a new" +
                    "profile for the remote client [Y/n] ", 'red'))
                if new_profile.lower() == 'n':
                    sys.exit()
            else:
                cprint("Profile found!", 'green')
                client.profile = profile

        elif not args.no_profiler:
            use_profile = input(colored(
                "Would you like to select a pre-generated profile " +
                "[y/N] ", 'green'))
            if use_profile.lower() == 'y':
                profile = profiler.interactive_chooser()
                if profile is None:
                    cprint("No profiles found... Will build new profile " +
                           "for remote client", 'red')
                else:
                    client.profile = profile

        lime = LimeDeploy(config, session, profiler)
        volatility = VolDeploy(config, session)

        lime.deploy()
        volatility.deploy()

        session.disconnect()
        logging.shutdown()


if __name__ == '__main__':
    Limeaide().main()
