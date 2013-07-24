import sys
sys.path.append('..')

def test_internal_networking_interface():
    from evilgenius.vagrant import VagrantBox, VBoxInternalNetworkingInterface

    testbox = VagrantBox(box="precise32", install_scripts=["echo 'Hello, World!'"],
                         name='testbox')

    iface = VBoxInternalNetworkingInterface(address="10.11.12.13", network_name="asdf")

    testbox.network_interfaces += [iface]

    assert "nic" in testbox.definition
    assert "asdf" in testbox.definition
