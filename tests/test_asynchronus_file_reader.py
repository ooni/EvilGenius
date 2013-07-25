from unittest import TestCase

class TestAsynchronusFileReader(TestCase):
    def test_file_reader_with_normal_output(self):
        import subprocess
        import Queue
        import time
        from evilgenius.util import AsynchronousFileReader

        p = subprocess.Popen(['ls', '-lah'], shell=True, stdout=subprocess.PIPE, cwd='/tmp/')
        stdout_queue = Queue.Queue()
        def print_line(line):
            pass

        stdout_reader = AsynchronousFileReader(fd=p.stdout, queue=stdout_queue, action=print_line)
        stdout_reader.start()

        stdout_reader.join()

    def test_file_reader_with_timed_output(self):
        import subprocess
        import Queue
        import time
        from evilgenius.util import AsynchronousFileReader

        p = subprocess.Popen(['ping -c 4 goatse.cx'], shell=True, stdout=subprocess.PIPE, cwd='/tmp/')
        stdout_queue = Queue.Queue()
        def print_line(line):
            pass

        stdout_reader = AsynchronousFileReader(fd=p.stdout, queue=stdout_queue, action=print_line)
        stdout_reader.start()

        stdout_reader.join()

    def test_output_result(self):
        import subprocess
        import Queue
        import time
        from evilgenius.util import AsynchronousFileReader

        p = subprocess.Popen(['echo "Hello, world!"'], shell=True, stdout=subprocess.PIPE, cwd='/tmp/')
        stdout_queue = Queue.Queue()
        def print_line(line):
            pass

        stdout_reader = AsynchronousFileReader(fd=p.stdout, queue=stdout_queue, action=print_line)
        stdout_reader.start()

        stdout_reader.join()

        output_lines = []
        while not stdout_queue.empty():
            output_lines += [stdout_queue.get()]

        self.assertTrue("Hello, world" in output_lines[0])

