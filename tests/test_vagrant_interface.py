import sys
sys.path.append('..')

def test_vagrant_status():
    from evilgenius.vagrant import VagrantController

    import tempfile

    testdir = tempfile.mkdtemp()

    c = VagrantController(root=testdir)
    c.init()

    print c.status()

    assert len(c.status().keys()) > 0
