import os
import sys

from os.path import join as opj
from glob import glob

from evilgenius.vagrant import VagrantBox

try:
    import yaml
except ImportError:
    print("[!] Evil Genius requires YAML")
    print("    Please install it from here:")
    print("    http://bitbucket.org/xi/pyyaml")
    sys.exit(1)


class ManagedResource(object):
    """
    I am a base class for all types of machines we want to manage within
    EvilGenius
    """
    def __init__(self, descriptor_path, controller):
        """
        Create Managed Resource, save path of descriptor and bind it to
        a :class:`evilgenius.vagrant.VagrantController` object

        Args:
            descriptor_path (str): Path to the descriptor file
            controller (:class:`evilgenius.vagrant.VagrantController`):
                VagrantController to bind to.
        """
        with open(descriptor_path) as f:
            self.config = yaml.load(f)

        self.id = os.path.basename(descriptor_path).replace(".yml", "")

        self.controller = controller

        # prepare instal scripts in order
        if type(self.config['before_install']) is list:
            before_install = self.config['before_install']
        else:
            before_install = [self.config['before_install']]

        if type(self.config['install']) is list:
            install = self.config['install']
        else:
            install = [self.config['install']]

        if type(self.config['after_install']) is list:
            after_install = self.config['after_install']
        else:
            after_install = [self.config['after_install']]

        self.box = VagrantBox(
            name=self.id,
            box=self.config['box'],
            before_install=before_install,
            install=install,
            after_install=after_install,
            network_scripts=[],
            script_folder=os.path.abspath(os.path.dirname(descriptor_path)))


class CensorshipProvider(ManagedResource):
    """
    Box doing censorship for the test network
    """
    def __init__(self, descriptor_path, controller):
        ManagedResource.__init__(self, descriptor_path=descriptor_path,
                                 controller=controller)

    def start(self):
        """
        Run the censorship provider's `run` command
        """
        self.controller.up(vm=self.id)
        self.controller.run_command(self.config.start)

    def stop(self):
        """
        Run the censorship provider's `stop` command
        """
        self.controller.run_command(self.config.stop)

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


class NetworkMeasurementInstrument(ManagedResource):
    """
    Box doing experiments in the simulated network
    """
    def __init__(self, descriptor_path, controller):
        ManagedResource.__init__(self, descriptor_path=descriptor_path,
                                 controller=controller)

    def run(self, logfile):
        """
        Run the network measurement instrument.
        """
        output_lines = self.controller.run_command(self.config['run'],
                                                   vm=self.box.name)
        with open(logfile, 'w') as f:
            for line in output_lines:
                f.write(line)


class Router(object):
    """
    Box that concentrates network measurement instruments and simplifies
    granting each of them network access
    """
    def __init__(self, controller):
        """
        Create router.

        Args:
            controller (:class:`evilgenius.vagrant.VagrantController`)
        """
        self.id = 'router'
        self.controller = controller

        setup_scripts = [
            "echo 1 > /proc/sys/net/ipv4/ip_forward",
        ]

        self.box = VagrantBox(name='router', install=setup_scripts,
                              box='precise32')


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
        self.censorship_provider_directory = \
            opj(self.resources_path, 'censorship-providers')
        self.network_measurement_directory = \
            opj(self.resources_path, 'network-measurement-instruments')
        self.censorship_providers = {}
        self.network_measurement_instruments = {}

        for cp_descriptor in glob(self.censorship_provider_directory +
                                  '/*/*.yml'):
            cp_id = os.path.basename(os.path.dirname(cp_descriptor))
            with open(cp_descriptor) as f:
                self.censorship_providers[cp_id] = yaml.load(f)

        for nm_descriptor in glob(self.network_measurement_directory +
                                  '/*/*.yml'):
            nm_id = os.path.basename(os.path.dirname(nm_descriptor))
            with open(nm_descriptor) as f:
                self.network_measurement_instruments[nm_id] = yaml.load(f)

    def list_censorship_providers(self):
        """
        Print out a list of all censorship providers we can find.
        """
        print "== [ Censorship Providers ] =="
        print ""
        for key, content in self.censorship_providers.items():
            print "%s:" % key
            print "   name: %s" % content['name']
            print "   description: %s" % content['description']
        print ""

    def list_network_measurement_instruments(self):
        """
        Print out a list of all network measurement instruments we can find.
        """
        print "== [ Network Measurement Instruments ] =="
        print ""
        for key, content in self.network_measurement_instruments.items():
            print "%s:" % key
            print "   name: %s" % content['name']
            print "   description: %s" % content['description']
        print ""
