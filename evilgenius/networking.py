import sys
import logging


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
    def __init__(self, address, peer_address, network_name):
        """
        Create an internal Networking Interface. Specific to VirtualBox.

        Args:
            address (string): IPv4 address with netmask, like "10.11.12.13/24"
            peer_address (string): IPv4 address with netmask, like
                "10.11.12.13/24"
            network_name (string): Name of the internal network to be used.
        """
        NetworkInterface.__init__(self, address)
        self.peer_address = peer_address
        self.network_name = network_name

    def config_lines(self, interface_number, vm_name):
        """
        Args:
            interface_number (int): Number of the virtual networking interface
            vm_name (str): name of the vm.

        Returns:
            list(str): Configuration lines for adding this Interface to
                the boxes definition.
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
    def __init__(self, network_name):
        """
        Create an internal Networking Interface. Specific to VirtualBox.
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

    def __init__(self, router=None, censorship_providers=[],
                 network_measurement_instruments=[]):
        """
        Create a network topology

        Args:
            router (:class:`evilgenius.resources.Router`): Router for the
                censorship simulation network
            censorship_providers (list): List of
                :class:`evilgenius.resources.CensorshipProvider` objects
            censorship_providers (list): List of
                :class:`evilgenius.resources.NetworkMeasurementInstrument`
                objects
        """
        self.router = router
        self.censorship_providers = censorship_providers
        self.network_measurement_instruments = network_measurement_instruments

    @property
    def vagrantfile(self):
        """
        Returns:
            str with the finished vagrantfile
        """

        # "patch" network_measurement instruments to the router

        _ip_ctr = 1
        _patch_ctr = 1

        router = self.router

        for n in self.network_measurement_instruments:

            nm_address = "10.11.12.%i/32" % _ip_ctr
            router_address = "10.11.12.%i/32" % (_ip_ctr + 1)

            n.box.network_interfaces += [
                VBoxInternalNetworkingInterface(
                    address=nm_address, peer_address=router_address,
                    network_name='eg_network_measurement_%i' % _patch_ctr)]
            router.box.network_interfaces += [
                VBoxInternalNetworkingInterface(
                    address=router_address, peer_address=nm_address,
                    network_name='eg_network_measurement_%i' % _patch_ctr)]
            n.box.network_scripts += ["ip r a %s dev eth1" % router_address]
            router.box.network_scripts += ["ip r a %s dev eth%i" %
                                           (nm_address, _patch_ctr)]

            n.box.network_scripts += ["while ip route del default; do :; done"]
            n.box.network_scripts += ["ip r a default via %s" %
                                      router_address.split("/")[0]]

            if _ip_ctr >= 254:
                logging.warn("Networks with more than 126 measurement \
                        instruments are not supported :(")
            _patch_ctr += 1
            _ip_ctr += 2

        # "patch" censorship providers to the router
        if len(self.censorship_providers) > 1:
            logging.error("Multiple censorship providers are not supported")
            sys.exit(0)

        router.box.network_interfaces += [
            VBoxInternalNetworkingInterface(
                address='10.11.13.1/24',
                peer_address="10.11.13.2/24",
                network_name='eg_censorship_provider_1')]
        self.censorship_providers[0].box.network_interfaces += [
            VBoxInternalNetworkingInterface(
                address='10.11.13.2/24',
                peer_address='10.11.13.l/24',
                network_name='eg_censorship_provider_1')]

        # announce route to network measurement instruments
        self.censorship_providers[0].box.network_scripts += \
            ["ip r a 10.11.12.0/24 via 10.11.13.1"]

        # route all traffic through censorship provider
        router.box.network_scripts += \
            ["while ip route del default; do :; done",
             "ip r a default via 10.11.13.2"]

        boxes = [n.box for n in self.network_measurement_instruments] +\
            [c.box for c in self.censorship_providers] + [router.box]

        result = 'Vagrant.configure("2") do |config|'
        for box in boxes:
            result += box.definition
        result += 'end'

        return result
