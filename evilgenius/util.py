import threading
import Queue

class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue, action):
        """
        initialize the AsynchronusFileReader.

        Args:
            fd(file-like object): File Descriptor, typically stdout or stderr
            queue(:class:`Queue.Queue`): Queue object where the output lines are stored
            action(callable): will be called for each line, think logging, etc.
        """
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        assert callable(action)

        self._action = action
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._action(line)
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()
