import multiprocessing
import signal
from tqdm.auto import tqdm

class StandaloneMultiThreadedUnit(object):
    r"""Holds a standalone multi-threaded unit to book and submit multiple processes.
        Can use local resource or batch resources depending on the config. 
    """

    def __init__(self, **kwargs):

        self.workers = kwargs.pop('workers', 8)
        self.use_unordered_mapping = kwargs.pop('use_unordered_mapping', False)

        # book multi tasks handler by multiprocessing.Pool
        def init_worker():
            # allow the subprocess to be notified by the interrupt signal
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.pool = multiprocessing.Pool(processes=self.workers, initializer=init_worker)
        self.args = []
    
    def book(self, arg: tuple):
        # accept one argument only
        self.args.append(arg)

    def run(self, func):
        try:
            imap = self.pool.imap if not self.use_unordered_mapping else self.pool.imap_unordered
            result = list(tqdm(imap(func, self.args), total=len(self.args)))
            return result
        except KeyboardInterrupt:
            self.pool.terminate()
            self.pool.join()
            return None
