#!/usr/bin/env python

import os
import sys
import subprocess

from distutils.spawn import find_executable
from glob import glob
from os.path import join as opj

import yaml

class VagrantBox(object):
    def __init__(self, name, box="precise32", install_scripts=[]):
        self.name = name
        self.box = box
        if not type(install_scripts) is list:
            install_scripts = [install_scripts]
        self.install_scripts = install_scripts

    def generate_ruby(self):
        provision_lines = ""

        for script in self.install_scripts:
            provision_lines += """
            probe.vm.provision :shell, :inline => "{script}"
            """.format(script=script)

        code = """
        config.vm.define :{name} do |{name}|
            probe.vm.box = "{box}"
            probe.vm.provider :virtualbox do |vb|
              vb.customize ["modifyvm", :id, "--nic2", "intnet"]
              vb.customize ["modifyvm", :id, "--intnet2", "probe"]
            end
            {provision_lines}
        end
        """.format(box=self.box, name=self.name, provision_lines=provision_lines)
        return code

class VagrantController(object):
    def __init__(self, root=None):
        if not root:
            root = os.getcwd()
        self.root = root
        self.vagrant_executable = find_executable('vagrant')
        if not self.vagrant_executable:
            print "[!] Vagrant does not appear to be installed."
            print "    Please download and install a copy of it here:"
            print "    http://downloads.vagrantup.com/"
            sys.exit(1)

    def init(self, vm=None):
        args = ['init']
        if vm:
            args += vm
        self._vagrant(args)

    def up(self, vm=None):
        args = ['up']
        if vm:
            args += vm
        self._vagrant(args)

    def destroy(self, vm=None):
        args = ['destroy']
        if vm:
            args += vm
        self._vagrant(args)

    def _vagrant(self, command):
        args = [self.vagrant_executable] + command
        p = subprocess.Popen(args, shell=True, cwd=self.root,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line,
        retval = p.wait()

class EvilGeniusResources(object):
    """
    I am responsible for keeping track of all Evil Genius resources.
    Currently the two kinds of resources in existance are:

    * Censorship providers: these are useful for creating a censorship
      environment.

    * Network measurement instruments: these are what is run to measure the
      censored network.
    """
    resources_path = os.path.abspath(opj(os.path.dirname(__file__), '..',
                                         'resources'))

    def __init__(self):
        self.censorship_provider_directory = opj(self.resources_path,
                                                 'censorship-providers')
        self.network_measurement_directory = opj(self.resources_path,
                                                 'network-measurement-instruments')

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

    def init_censorship_provider(self, name):
        vagrant_box = VagrantBox(name,
                                 self.censorship_providers[name]['box'],
                                 self.censorship_providers[name]['install'])
        print vagrant_box.generate_ruby()
    
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
    evil_genius_resources.init_censorship_provider('dns-censorship')

    if args.list:
        evil_genius_resources.list_censorship_providers()
        evil_genius_resources.list_network_measurement_instruments()
