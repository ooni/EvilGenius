from unittest import TestCase
import os


class TestVagrantInterface(TestCase):
    def test_vagrant_init(self):
        from evilgenius.vagrant import VagrantController
        import tempfile

        tempdir = tempfile.mkdtemp()

        cont = VagrantController(root=tempdir)

        cont.init()

        with open(os.path.join(tempdir, 'Vagrantfile')) as f:
            self.assertGreater(len(f.read()), 0)

    def test_vagrant_status(self):
        from evilgenius.vagrant import VagrantController
        import tempfile

        tmpdir = tempfile.mkdtemp()
        cont = VagrantController(root=tmpdir)

        def mock_status_output(command):
            return (0, ['Current machine states:\n', '\n',
                        'default                  not created (virtualbox)\n',
                        '\n', 'The environment has not yet been created. Run `vagrant up` to\n',
                        'create the environment. If a machine is not created, only the\n',
                        'default provider will be shown. So if a provider is not listed,\n',
                        'then the machine is not created for that environment.\n'])
        cont._vagrant = mock_status_output

        self.assertEqual(cont.status(), {'default': 'not created'})
        self.assertEqual(cont.status(vm='default'), 'not created')
