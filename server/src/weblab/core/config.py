import time
import threading
from collections import MutableMapping

class DbConfig(MutableMapping):
    """Dictionary-like configuration object with local cache"""
    def __init__(self, method, timeout = 10):
        self.method = method
        self.timeout = timeout
        
        self.last_time = 0
        self.lock = threading.Lock()
        self.values = None

    def _get_keys(self):
        # The following code takes ~20% less with the lock
        # >>> timeit.timeit(lambda : requests.get("http://localhost/weblab/web//webclient/"), number=100)
        with self.lock:
            if (time.time() - self.last_time) > self.timeout:
                self.values = self.method()
                self.last_time = time.time()
            return self.values

    def __getitem__(self, name):
        return self._get_keys().__getitem__(name)

    def __setitem__(self, name, value):
        return value
        
    def __delitem__(self, name):
        pass
        
    def __iter__(self, name):
        return self._get_keys().__iter__(name)
    
    def __len__(self):
        return self._get_keys().__len__()

