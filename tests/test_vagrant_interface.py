import sys
sys.path.append('..')

def test_vagrant_status():
    from evilgenius.vagrant import VagrantController

    import tempfile

    testdir = tempfile.mkdtemp()

    c = VagrantController(root=testdir)
    c.init()
    assert len(c.status()) > 0
    c.up()
    assert c.status()['default'] == 'running'
    a = c.run_command('echo "Hello, World!"')
    assert a == ['Hello, World!\n']
    c.destroy()
    assert c.status()['default'] == 'not created'
