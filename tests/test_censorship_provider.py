from unittest import TestCase

class TestCensorshipProvider(TestCase):
    def asdf_test_censorship_provider_creation(self):
        import os
        import tempfile

        from evilgenius.resources import CensorshipProvider
        from evilgenius.vagrant import VagrantController, VagrantFile

        path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'resources',
                        'censorship-providers', 'dns-censorship',
                        'dns-censorship.yml'))

        vagrant_dir = tempfile.mkdtemp()
        cont = VagrantController(root=vagrant_dir)
        cens = CensorshipProvider(descriptor_path=path, controller=cont)
        vfile = VagrantFile(boxes=[cens.box], network=None)
        with open(os.path.join(vagrant_dir, 'Vagrantfile'), 'wb') as f:
            f.write(vfile.content)
        cont.create_box(box=cens.box)

        self.assertTrue(cens.box is not None)
        self.assertTrue(len(cont.status().keys()) > 0)
