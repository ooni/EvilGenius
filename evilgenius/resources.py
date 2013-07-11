import os
import sys

from os.path import join as opj
from glob import glob

from evilgenius.vagrant import VagrantBox

try:
    import yaml
except ImportError:
    print "[!] Evil Genius requires YAML"
    print "    Please install it from here:"
    print "    http://bitbucket.org/xi/pyyaml"
    sys.exit(1)

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
