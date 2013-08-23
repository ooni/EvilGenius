import re
import sys
import os
import subprocess
import logging
from Queue import Queue

from distutils.spawn import find_executable

from evilgenius.util import AsynchronousFileReader
from evilgenius.networking import VBoxInternalNetworkingInterface, NetworkTopology


class VagrantBox(object):
    def __init__(self, name, box="precise32", install_scripts=[], script_folder=None):
        # We strip the "-" char, because Vagrant does not like it since it
        # interprets it as an operator.
        self.name = name.replace("-", "")

        self.network_interfaces = []
        self.box = box
        if not type(install_scripts) is list:
            install_scripts = [install_scripts]
        self.install_scripts = install_scripts
        self.script_folder = script_folder

    @property
    def definition(self):
        provision_lines = ""

        # Prepare provisioning lines

        install_scripts = self.install_scripts

        # Prepare network interfaces
        network_configuration_lines = ""
        interface_number = 2
        for iface in self.network_interfaces:
            network_configuration_lines += iface.config_lines(interface_number, self.name)
            install_scripts.append("ip a add %s dev eth%i" % (iface.address, interface_number - 1))
            install_scripts.append("ip l set eth%i up" % (interface_number - 1,))
            interface_number += 1


        for script in install_scripts:
            provision_lines += """
            {name}.vm.provision :shell, :inline => "{script}"
            """.format(script=script.replace('"', '\\\"'), name=self.name)


        if self.script_folder:
            script_folder_line = "{name}.vm.synced_folder \"{script_folder}\", \"/scripts\"".format(script_folder=self.script_folder, name=self.name)
        else:
            script_folder_line = ""


        code = """
        config.vm.define :{name} do |{name}|
            {name}.vm.box = "{box}"
            {script_folder_line}
            {provision_lines}
            {network_configuration_lines}
        end
        """.format(box=self.box, name=self.name,
                   provision_lines=provision_lines,
                   network_configuration_lines=network_configuration_lines,
                   script_folder_line=script_folder_line)
        return code


class VagrantController(object):
    def __init__(self, root=None):
        if not root:
            root = os.getcwd()
        self.root = root
        self.vagrant_executable = find_executable('vagrant')
        if not self.vagrant_executable:
            print("[!] Vagrant does not appear to be installed.")
            print("    Please download and install a copy of it here:")
            print("    http://downloads.vagrantup.com/")
            sys.exit(1)

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
        logging.info("Executing: %s %s" % (self.vagrant_executable, " ".join(command)))
        args = [self.vagrant_executable] + command
        p = subprocess.Popen(args, shell=False, cwd=self.root,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        def log_output(line):
            logging.debug("[v] "+line.strip())

        stdout_queue = Queue()
        stdout_reader = AsynchronousFileReader(fd=p.stdout, queue=stdout_queue, action=log_output)

        stdout_reader.start()
        output_lines = []
        while not stdout_reader.eof():
            while not stdout_queue.empty():
                output_lines += [stdout_queue.get()]

        stdout_reader.join()
        return (p.returncode, output_lines)
