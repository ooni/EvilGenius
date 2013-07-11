import os
import subprocess

from distutils.spawn import find_executable

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
