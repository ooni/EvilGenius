#!/usr/bin/env python

import os

from glob import glob
from os.path import join as opj

import yaml

class EvilGeniusResources(object):
    resources_path = os.path.abspath(opj(os.path.dirname(__file__), '..', 'resources'))

    def __init__(self):
        self.censorship_provider_directory = opj(self.resources_path, 'censorship-providers')
        self.network_measurement_directory = opj(self.resources_path, 'network-measurement-instruments')

        self.censorship_providers = {}
        self.network_measurement_instruments = {}

        for cp_descriptor in glob(self.censorship_provider_directory + '/*/*.yml'):
            cp_id = os.path.basename(os.path.dirname(cp_descriptor))
            with open(cp_descriptor) as f:
                self.censorship_providers[cp_id] = yaml.load(f)

        for nm_descriptor in glob(self.network_measurement_directory + '/*/*.yml'):
            nm_id = os.path.basename(os.path.dirname(nm_descriptor))
            with open(nm_descriptor) as f:
                self.network_measurement_instruments[nm_id] = yaml.load(f)

    def list_censorship_providers(self):
        print "== [ Censorship Providers ] =="
        print ""
        for key, content in self.censorship_providers.items():
            print "%s:" % key
            print "   name: %s" % content['name']
            print "   description: %s" % content['description']
        print ""

    def list_network_measurement_instruments(self):
        print "== [ Network Measurement Instruments ] =="
        print ""
        for key, content in self.network_measurement_instruments.items():
            print "%s:" % key
            print "   name: %s" % content['name']
            print "   description: %s" % content['description']
        print ""

def parse_arguments():
    try:
        import argparse
    except ImportError:
        print "[!] Error! Evil Genius requires argparse."
        print ""
        print "argparse is found in python >= 2.7."
        print "If you do not wish to update to a modern version of python " \
              "you must manually install the argparse module."

    parser = argparse.ArgumentParser()
    parser.add_argument("--network-measurement", "-n",
                        help="Run the specified network measurement instruments",
                        action='append')
    parser.add_argument("--censorship-providers", "-c",
                        help="Run the network measurement with the specified censorship providers",
                        action='append')
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all available network measurement instruments and censorship providers")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")

    return parser.parse_args()

if __name__ == "__main__":

    args = parse_arguments()
    evil_genius_resources = EvilGeniusResources()

    if args.list:
        evil_genius_resources.list_censorship_providers()
        evil_genius_resources.list_network_measurement_instruments()
