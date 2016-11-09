#############################################################
# 2016-10-18: tomes_controller.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: This is a test for setup of a Docker environment
##############################################################

import json
import argparse
from TomesServer.tomes_client import TomesClient


class TomesController:
    def __init__(self):
        self._arg_parse()

    def _arg_parse(self):
        parser = argparse.ArgumentParser(description='Controls the TOMES tool')
        parser.add_argument('--readpst', '-r', dest='tomes_readpst', required=False, action='store_true',
                            help='activate the readpst module. Enter --help_readpst to see module specific options')
        parser.add_argument('--darcmail', '-d', dest='tomes_darcmail', required=False,
                            help='activate the darcmail module. Enter --help_darcmail to see module specific options')
        parser.add_argument('--tagger', '-t', dest='tomes_tagger', required=False,
                            help='activate the tagger module.  Enter --help_tagger to see module specific options')
        parser.add_argument('--help_readpst', '-hr', dest='help_readpst', required=False)
        parser.add_argument('--help_darcmail', '-hd', dest='help_darcmail', required=False)
        parser.add_argument('--help_tagger', '-ht', dest='help_tagger', required=False)

        parser.add_argument('--account_name', '-ra', dest='account_name')
        parser.add_argument('--target_file', '-tp', dest='target_file')

        args = parser.parse_args()
        argdict = vars(args)

        if argdict['tomes_readpst']:
            self._package_readpst_args(argdict)

    def _package_readpst_args(self, argdict):
        json_package = {}
        json_package[0] = {"account_name": "/home/tomes/data/mboxes/{}".format(argdict["account_name"]),
                           "target_file": "/home/tomes/data/pst/{}".format(argdict["target_file"])}
        self._send_package(json_package)

    def _send_package(self, package):
        tc = TomesClient()
        tc.send_package(json.dumps(package))
        print(tc.received)


if __name__ == "__main__":
    TC = TomesController()
