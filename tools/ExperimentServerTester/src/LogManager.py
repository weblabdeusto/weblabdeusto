'''
Created on 03/12/2009

@author: lrg
'''

import LogEntry
import time
import threading

class LogManager(object):
    
    def __init__(self):
        self.mLock = threading.RLock()
        self.mNextId = 1
        self.mEntriesList = [] # 0 based, unlike the ids which are 1 based.
        
    def clear(self):
        with self.mLock:
            self.mNextId = 1
            self.mEntriesList = []
        
    def create_entry(self, sent, recv, time = time.strftime("%H:%M:%S")):
        """
        Creates a new log entry and returns it.
        """
        with self.mLock:
            log_entry = LogEntry.LogEntry(sent, recv, self.mNextId, time)
            self.mNextId += 1
            self.mEntriesList.append(log_entry)
            return log_entry
        
    def get_entry_by_id(self, id):
        """
        Returns the entry with the specified id. Entries are given a unique, 
        increasing id when created. First entry is given a 1 as an id.
        """
        with self.mLock:
            entry = self.mEntriesList[id-1]
            return entry
    
    def get_next_id(self):
        """
        Returns the id that will be given to the next entry to be created.
        """
        with self.mLock:
            return self.mNextId