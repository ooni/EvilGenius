import os
import sys
sys.path.append('..')

def test_network_measurement_instruments():
    from evilgenius.vagrant import VagrantController, VagrantFile
    from evilgenius.resources import NetworkMeasurementInstrument

    import tempfile

    testdir = tempfile.mkdtemp()
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'resources',
                     'network-measurement-instruments', 'ping',
                     'ping.yml'))

    cont = VagrantController(root=testdir)
    netm = NetworkMeasurementInstrument(controller=cont, descriptor_path=path)

    cont.init_modular_vagrantfile()
    cont.create_box(box=netm.box)
    cont.up(vm=netm.id)
    assert cont.status(vm=netm.id) == 'running'
    assert len(netm.run()) > 5
    cont.destroy(vm=netm.id)
