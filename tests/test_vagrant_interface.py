from unittest import TestCase
import os

from evilgenius.vagrant import VagrantController
import tempfile



class TestVagrantInterface(TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.cont = VagrantController(root=self.tempdir)

    def test_vagrant_init(self):
        self.cont.init()

        with open(os.path.join(self.tempdir, 'Vagrantfile')) as f:
            self.assertGreater(len(f.read()), 0)

    def test_vagrant_status(self):
        def mock_status_output(command):
            return (0, ['Current machine states:\n', '\n',
                        'default                  not created (virtualbox)\n',
                        '\n', 'The environment has not yet been created. Run `vagrant up` to\n',
                        'create the environment. If a machine is not created, only the\n',
                        'default provider will be shown. So if a provider is not listed,\n',
                        'then the machine is not created for that environment.\n'])
        self.cont._vagrant = mock_status_output

        self.assertEqual(self.cont.status(), {'default': 'not created'})
        self.assertEqual(self.cont.status(vm='default'), 'not created')

    def test_vagrant_ssh(self):
        self.cont.init()
        self.cont.up()

        output = self.cont.run_command("echo 'spamham'")

        self.assertEqual(''.join(output), "spamham\n")

        self.cont.destroy()
