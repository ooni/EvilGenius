import re
import sys
import os
import subprocess
from Queue import Queue

from distutils.spawn import find_executable

from evilgenius.util import AsynchronousFileReader


class NetworkInterface(object):
    """
    Represents a virtual Network Interface
    """
    def __init__(self, address=None):
        """
        Creates a virtual network Interface

        Args:
            address (string): IPv4 address with netmask, like "10.11.12.13/24"
        """
        if address:
            self.address = address  # TODO check validity

class VBoxInternalNetworkingInterface(NetworkInterface):
    """
    Represents a internal Networking Interface specific to VirtualBox
    """
    def __init__(self, address, network_name):
        """
        Create an internal Networking Interface. Specific to VirtualBox.

        Args:
            address (string): IPv4 address with netmask, like "10.11.12.13/24"
            network_name (string): Name of the internal network to be used.
        """
        NetworkInterface.__init__(self, address)
        self.network_name = network_name


    def config_lines(self, interface_number, vm_name):
        """
        Args:
            interface_number (int): Number of the virtual networking interface
            vm_name (str): name of the vm.

        Returns:
            list(str): Configuration lines for adding this Interface to the boxes
                definition.
        """
        code = """
        {vm_name}.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--nic{interface_number}", "intnet"]
            vb.customize ["modifyvm", :id, "--intnet{interface_number}", "{network_name}"]
        end""".format(interface_number=interface_number, vm_name=vm_name,
                      network_name=self.network_name)

        return code


class VBoxNatInterface(NetworkInterface):
    """
    Represents a internal Networking Interface specific to VirtualBox
    """
    def __init__(self):
        """
        Create an internal Networking Interface. Specific to VirtualBox.

        Args:
            address (string): IPv4 address with netmask, like "10.11.12.13/24"
            network_name (string): Name of the internal network to be used.
        """
        NetworkInterface.__init__(self)
        self.network_name = network_name


    def config_line(self, interface_number, vm_name):
        """
        Args:
            interface_number (int): Number of the virtual networking interface
            vm_name (str): name of the vm.

        Returns:
            string: Configuration line for adding this Interface to the boxes
                definition.
        """

class NetworkTopology(object):
    """
    This class shall be used to store the topology of the network.
    """

    def __init__(self):
        self.censorship_providers = []
        self.network_measurement_instruments = []

    @property
    def router(self):
        """
        Returns:
            :class:`evilgenius.vagrant.VagrantBox`

            the router to be used for this given network topology.
        """
        #TODO add actual router
        return VagrantBox(box='precise32', name='router', install_scripts=[])

    @property
    def vagrantfile(self):
        """
        Returns:
            :class:`evilgenius.vagrant.VagrantFile` with all the boxes, nicely
                patched together and ready to pull up
        """

        # "patch" everything together
        # TODO "patch" network_measurement instruments to the router

        _ip_ctr = 1
        _patch_ctr = 1

        router = self.router

        for n in self.network_measurement_instruments:
            n.box.network_interfaces += [VBoxInternalNetworkingInterface(address='10.11.12.%i'%_ip_ctr, network_name='eg_network_measurement_%i'%_patch_ctr)]
            _ip_ctr += 1
            router.network_interfaces += [VBoxInternalNetworkingInterface(address='10.11.12.%i'%_ip_ctr, network_name='eg_network_measurement_%i'%_patch_ctr)]
            _patch_ctr += 1
            _ip_ctr += 1


        # TODO "chain" censorship_providers

        boxes = [n.box for n in self.network_measurement_instruments] + [c.box for c in self.censorship_providers] + [router]
        return VagrantFile(boxes=boxes)


class VagrantFile(object):
    def __init__(self, boxes):
        """
        Args:

            boxes (list): a list of :class:`evilgenius.vagrant.VagrantBox`
                instances.
        """
        if type(boxes) is list:
            self.boxes = boxes
        else:
            self.boxes = [boxes]

    @property
    def content(self):
        """
        Returns:
            string.

            the content of the Vagrantfile.
        """
        # pref
        result = 'Vagrant.configure("2") do |config|'
        for box in self.boxes:
            result += box.definition
        result += 'end'

        return result


class VagrantBox(object):
    def __init__(self, name, box="precise32", install_scripts=[]):
        # We strip the "-" char, because Vagrant does not like it since it
        # interprets it as an operator.
        self.name = name.replace("-", "")

        self.network_interfaces = []
        self.box = box
        if not type(install_scripts) is list:
            install_scripts = [install_scripts]
        self.install_scripts = install_scripts

    @property
    def definition(self):
        provision_lines = ""

        # Prepare provisioning lines
        for script in self.install_scripts:
            provision_lines += """
            {name}.vm.provision :shell, :inline => "{script}"
            """.format(script=script, name=self.name)

        # Prepare network interfaces
        network_configuration_lines = ""
        interface_number = 2
        for iface in self.network_interfaces:
            network_configuration_lines += iface.config_lines(interface_number, self.name)
            interface_number += 1


        code = """
        config.vm.define :{name} do |{name}|
            {name}.vm.box = "{box}"
            {provision_lines}
            {network_configuration_lines}
        end
        """.format(box=self.box, name=self.name,
                   provision_lines=provision_lines,
                   network_configuration_lines=network_configuration_lines)
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


    def init_modular_vagrantfile(self):
        """
        Initializes a Vagrant directory so that all files with names ending
        on ".vagrant.rb" are loaded by vagrant.
        """
        with open(os.path.join(self.root, 'Vagrantfile'), 'wb') as f:
            f.write("Dir.glob('*.vagrant.rb') {|file| load file}")

    def create_box(self, box):
        """
        Creates a new Vagrant box. If the box already exists it will raise an
        error.

        Args:

            box (:class:`evilgenius.vagrant.VagrantBox`): the vagrant box to be
                created. Will generate the appropriate VagrantFile for the
                specified box and initialize the box.
        """
        vfile = VagrantFile(box, None)  # TODO: add NetworkTopology Support
        f = open(os.path.join(self.root, box.name + '.vagrant.rb'), 'wb')
        f.write(vfile.content)
        f.close()

    def init(self, vm=None):
        """
        Calls the "vagrant init" command.
        """
        args = ['init']
        if vm:
            args += [vm]
        self._vagrant(args)

    def up(self, vm=None):
        """
        Calls the vagrant up command
        """
        args = ['up']
        if vm:
            args += [vm]
        self._vagrant(args)

    def destroy(self, vm=None):
        """
        Calls the vagrant destroy command
        """
        args = ['destroy']
        if vm:
            args += [vm]

        # use the --force, vagrant! (disables the y/N question vagrant asks)
        args += ['--force']

        self._vagrant(args)

    def run_command(self, command, vm=None):
        """
        Runs a command on a vagrant managed vm.

        Args:

            command: command to be executed

            vm: name of the vm

        Returns:

            list: list of output lines
        """
        args = ['ssh']
        if vm:
            args += [vm]
        args += ['-c', command]

        retval, output_lines = self._vagrant(args)

        return output_lines

    def status(self, vm=None):
        """
        Get vm statuses

        Returns:
            status: vm names and their current status. if vm is passed,
                return just the status of the vm.

        """
        args = ['status']
        output_lines = self._vagrant(args)[1]

        state = 1

        RUNNING = 'running' # vagrant up
        NOT_CREATED = 'not created' # vagrant destroy
        POWEROFF = 'poweroff' # vagrant halt
        ABORTED = 'aborted' # The VM is in an aborted state
        SAVED = 'saved' # vagrant suspend
        STATUSES = (RUNNING, NOT_CREATED, POWEROFF, ABORTED, SAVED)

        statuses = {}

        def parse_provider_line(line):
            m = re.search(r'^\s*(?P<value>.+?)\s+\((?P<provider>[^)]+)\)\s*$',
                        line)
            if m:
                return m.group('value'), m.group('provider')
            else:
                return line.strip(), None

        for line in output_lines:
            if state == 1 and re.search('^Current (VM|machine) states:', line.strip()):
                state = 2 # looking for the blank line
            elif state == 2 and line.strip() == '':
                state = 3 # looking for machine status lines
            elif state == 3 and line.strip() != '':
                vm_name_and_status, provider = parse_provider_line(line)
                # Split vm_name from status. Only works for recognized statuses.
                m = re.search(r'^(?P<vm_name>.*?)\s+(?P<status>' +
                                '|'.join(STATUSES) + ')$',
                                vm_name_and_status)
                if not m:
                    raise Exception('ParseError: Failed to properly parse vm name and status from line.', line, output)
                else:
                    statuses[m.group('vm_name')] = m.group('status')
            elif state == 3 and not line.strip():
                break

        if not vm:
            return statuses
        else:
            return statuses[vm]

    def _vagrant(self, command):
        """
        calls the vagrant executable

        Args:

            command: list or string containing the parameters for vagrant

        Returns:

            Tuple consisting of the return value and a list of output lines
        """
        # print("Executing: %s %s" % (self.vagrant_executable, " ".join(command)))
        args = [self.vagrant_executable] + command
        p = subprocess.Popen(args, shell=False, cwd=self.root,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def log_output(line):
            print line.strip()

        stdout_queue = Queue()
        stdout_reader = AsynchronousFileReader(fd=p.stdout, queue=stdout_queue, action=log_output)

        stdout_reader.start()
        output_lines = []
        while not stdout_reader.eof():
            while not stdout_queue.empty():
                output_lines += [stdout_queue.get()]

        stdout_reader.join()
        return (p.returncode, output_lines)
