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


class CensorshipProvider(object):
    def __init__(self, descriptor_path, controller):
        with open(descriptor_path) as f:
            self.config = yaml.load(f)

        self.id = os.path.basename(os.path.dirname(descriptor_path))\
            .replace("-", "")

        self.controller = controller

        # prepare instal scripts in order
        if type(self.config['before_install']) is list:
            install_scripts = self.config['before_install']
        else:
            install_scripts = [self.config['before_install']]

        if type(self.config['install']) is list:
            install_scripts.extend(self.config['install'])
        else:
            install_scripts.append(self.config['install'])

        if type(self.config['after_install']) is list:
            install_scripts.extend(self.config['after_install'])
        else:
            install_scripts.append(self.config['after_install'])

        self.box = VagrantBox(
            name=self.id,
            box=self.config['box'],
            install_scripts=install_scripts)

    def start(self):
        """
        Starts the censorship provider.
        """
        pass

    def stop(self):
        """
        Stops the censorship provider and runs all the commands to be run in
        the stop phase.
        """
        pass

    def status(self):
        """
        Returns:

            string.

            'running' -- the provider is running.

            'poweroff' -- the provider exists, but is not running.

            'not created' -- the provider has not been created.

            'aborted' -- the provider has been terminated abruptly.

            'saved' -- the provider has been suspended.
        """

        return self.controller.status(vm=self.id)

        pass


class NetworkMeasurementInstrument(object):
    def __init__(self, descriptor_path):
        pass

    def run(self):
        """
        Run the network measurement instrument.
        """
        pass


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
        print vagrant_box.definition

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
