#!/bin/python

import sys, datetime, os, argparse, getpass
from lime_deploy import LimeDeploy
from client import Client


class Limeaide(object):
    """Deploy LiME LKM to remote host in order to scrape RAM"""

    _version = "1.0.1"

    def __init__(self):
        super(Limeaide, self).__init__()
        self.lime_dir = './tools/LiME/src/'
        self.tools_dir = './tools/'
        self.output_dir = './output/'

    def check_tools(self):
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        if not os.path.isdir(self.lime_dir):
            if not os.path.isdir(self.tools_dir):
                os.mkdir(self.tools_dir)
            sys.exit("Please download LiME and place in the ./tools/ dir")

    def get_client(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("remote", help="remote host IP")

        parser.add_argument("-s", "--sudoer", help="use a sudo user instead default: root")
        parser.add_argument("-o", "--output", help="name the outputfile")
        args = parser.parse_args()

        client = Client()
        client.ip = args.remote
        if args.sudoer != None:
            client.user = args.sudoer
            client.is_sudoer = True
        if args.output != None:
            client.output = args.output

        return client

    def main(self):
        print("Welcome to LiMEaide v%s " %(self._version))
        self.check_tools()
        client = self.get_client()
        print("Attempting secure connection %s@%s" %(client.user, client.ip))
        print("Password for %s:" %client.user)
        client.pass_ = getpass.getpass()

        LimeDeploy(client).main()

if __name__ == '__main__':
    Limeaide().main()
