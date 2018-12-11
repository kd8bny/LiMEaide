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

from datetime import datetime
import configparser
from termcolor import cprint, colored
import os
import sys
import urllib.request
import zipfile
import shutil
import logging


class Config:

    __version__ = "1"

    def __init__(self):
        super(Config, self).__init__()
        # Internal Resources
        self.lime_version = '1.8.0.1'
        self.config_file = '.limeaide'
        self.manifest = 'manifest.json'
        self.lime_dir = './tools/LiME/src/'
        self.tools_dir = './tools/'
        self.output_dir = './output/'
        self.profile_dir = './profiles/'
        self.log_dir = './logs/'
        self.scheduled_pickup_dir = './scheduled_jobs/'

        # External Resources
        self.lime_rdir = './.limeaide_working/'

        self.date = None
        self.volatility_dir = None
        self.output = None
        self.compress = None
        self.format = None
        self.digest = None

    def set_date(self):
        self.date = datetime.strftime(datetime.today(), "%Y_%m_%dT%H_%M_%S")

    def setup_logging(self):
        """Setup logging to file and initial logger"""
        logging.basicConfig(
            level=logging.INFO, filename='{0}{1}.log'.format(
                self.log_dir, self.date))
        self.logger = logging.getLogger(__name__)

    def __update_config__(self):
        cprint("Updating Configuration", 'green')
        # self.logger.info("Updating config file")
        # self.format = 'lime'
        # self.digest = 'sha1'

        # default_config = configparser.ConfigParser()
        # default_config['MANIFEST'] = {}
        # default_config['MANIFEST']['version'] = str(self.__version__)
        # default_config.set('DEFAULT', 'volatility', self.volatility_dir)
        # default_config.set('DEFAULT', 'output', self.output)
        # default_config.set('DEFAULT', 'compress', self.compress)
        # default_config.set('DEFAULT', 'format', self.format)
        # default_config.set('DEFAULT', 'digest', self.digest)
        # with open('.limeaide', 'w+') as config_file:
        #     config.write(config_file)
        pass

    def __download_lime__(self):
        cprint("Downloading LiME", 'green')
        try:
            urllib.request.urlretrieve(
                "https://github.com/kd8bny/LiME/archive/" +
                "v{}.zip".format(
                    self.lime_version), filename="./tools/lime_master.zip")
            zip_lime = zipfile.ZipFile("./tools/lime_master.zip", 'r')
            zip_lime.extractall(self.tools_dir)
            zip_lime.close()
            shutil.move(
                './tools/LiME-{}'.format(self.lime_version), './tools/LiME/')
        except urllib.error.URLError:
            sys.exit(colored(
                "LiME failed to download. Check your internet connection" +
                " or place manually", 'red'))

    def __write_new_config__(self):
        default_config = configparser.ConfigParser()
        default_config['MANIFEST'] = {}
        default_config['MANIFEST']['version'] = self.__version__
        default_config.set('DEFAULT', 'volatility', '')
        default_config.set('DEFAULT', 'output', 'dump.lime')
        default_config.set('DEFAULT', 'compress', 'False')
        default_config.set('DEFAULT', 'format', 'lime')
        default_config.set('DEFAULT', 'digest', 'sha1')
        with open(self.config_file, 'w') as configfile:
            default_config.write(configfile)

    def __update_vol_dir__(self):
        cprint("Volatility directory missing.", 'red')
        cprint("Please provide a path to your Volatility directory." +
               "\ne.g. '~/volatility/'" +
               "\n[q] to never ask again: ", 'green')

        path_ext = '/volatility/plugins/overlays/linux/'

        while True:
            path = input(":")
            if path == 'q':
                path = 'None'
                path_ext = ''
                break
            elif os.path.isdir(path):
                break
            else:
                cprint(
                    "Entered directory does not exist. Please enter" +
                    " again", 'red')

        self.volatility_dir = path + path_ext

        default_config = configparser.ConfigParser()
        default_config.read(self.config_file)
        default_config.set(
            'DEFAULT', 'volatility', self.volatility_dir)
        with open(self.config_file, 'w+') as configfile:
            default_config.write(configfile)

    def check_directories(self):
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        if not os.path.isdir(self.profile_dir):
            os.mkdir(self.profile_dir)

        if not os.path.isdir(self.tools_dir):
            os.mkdir(self.tools_dir)

        if not os.path.isdir(self.scheduled_pickup_dir):
            os.mkdir(self.scheduled_pickup_dir)

        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)

        if not os.path.isdir(self.lime_dir):
            self.__download_lime__()

    def read_config(self):
        """Read default configuration."""
        if not os.path.isfile(self.config_file):
            self.__write_new_config__()

        default_config = configparser.ConfigParser()
        default_config.read(self.config_file)
        try:
            if int(self.__version__) > int(default_config['MANIFEST']['version']):
                self.__update_config__()

            else:
                self.volatility_dir = default_config['DEFAULT']['volatility']
                self.output = default_config['DEFAULT']['output']
                self.compress = default_config['DEFAULT']['compress']
                self.format = default_config['DEFAULT']['format']
                self.digest = default_config['DEFAULT']['digest']

        except KeyError:
            self.__update_config__()

        if self.volatility_dir != 'None':
            if not self.volatility_dir or not os.path.isdir(
                    self.volatility_dir):
                self.__update_vol_dir__()

    def configure(self):
        self.set_date()
        self.check_directories()
        self.setup_logging()
        self.read_config()
