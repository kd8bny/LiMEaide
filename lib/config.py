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
    def __init__(self):
        super(Config, self).__init__()

        #self.ascii = 
        self.lime_version = '1.8.0.1'
        self.date = datetime.strftime(
            datetime.today(), "%Y_%m_%dT%H_%M_%S_%f")
        self.volatility_profile_dir = None
        self.lime_dir = './tools/LiME/src/'
        self.tools_dir = './tools/'
        self.output_dir = './output/'
        self.profile_dir = './profiles/'
        self.log_dir = './logs/'
        self.scheduled_pickup_dir = './scheduled_jobs/'

        self.defaults = None

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
                "or place manually", 'red'))

    def __write_new_config__(self):
        config = configparser.RawConfigParser()
        config.set('DEFAULT', 'volatility', '')
        config.set('DEFAULT', 'output', '')
        config.set('DEFAULT', 'compress', '')
        with open('.limeaide', 'w+') as config_file:
            config.write(config_file)

    def __update_vol_dir__(self, vol_dir):
        cprint(
            "Volatility directory missing. Current directory is:", 'red')
        cprint("{}".format(vol_dir), 'blue')
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
                    "again", 'red')

        self.defaults.set('DEFAULT', 'volatility', path + path_ext)
        with open('.limeaide', 'w+') as configfile:
            self.defaults.write(configfile)

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

        vol_dir = self.defaults['DEFAULT']['volatility']
        if vol_dir == 'None':
            continue
        elif not vol_dir or not os.path.isdir(vol_dir):
            self.__update_vol_dir__()

    def read_config(self):
        """Read default configuration."""
        if not os.path.isfile('.limeaide'):
            self.__write_new_config__()

        self.defaults = configparser.ConfigParser()
        self.defaults.read('.limeaide')

    def setup_logging(self):
        """Setup logging to file and initial logger"""
        logging.basicConfig(
            level=logging.INFO, filename='{0}{1}.log'.format(
                self.log_dir, self.date))
        self.logger = logging.getLogger(__name__)

    def configure(self):
        self.read_config()
        self.check_directories()
        self.setup_logging()
