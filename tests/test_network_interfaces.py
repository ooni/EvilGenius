from unittest import TestCase

class TestNetworkingInterfaces(TestCase):
    def test_internal_networking_interface(self):
        from evilgenius.vagrant import VagrantBox, VBoxInternalNetworkingInterface

        testbox = VagrantBox(box="precise32", install_scripts=["echo 'Hello, World!'"],
                            name='testbox')

        iface = VBoxInternalNetworkingInterface(address="10.11.12.13", peer_address="10.11.12.14", network_name="asdf")

        testbox.network_interfaces += [iface]

        self.assertTrue("nic" in testbox.definition)
        self.assertTrue("asdf" in testbox.definition)
