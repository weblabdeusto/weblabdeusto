'''
Created on 03/12/2009

@author: lrg
'''

import time

class LogEntry(object):
    """
    Represents a log entry. A log entry has two main fields, sent and
    received. It also has an associated datetime and an identifier
    which will generally be unique.
    """
    
    def __init__(self, sent, recv, num, time = time.strftime("%H:%M:%S")):
        self.mSent = sent
        self.mRecv = recv
        self.mTime = time
        self.mNum = num
        
    Num = property( lambda(self): self.mNum )
    
    Sent = property( lambda(self): self.mSent )
    
    Received = property( lambda(self) : self.mRecv )
    
    Time = property( lambda(self) : self.mTime )
    
    def _get_short_sent(self):
        return self.mSent.replace("\n", " | ")
    
    def _get_short_received(self):
        return self.mRecv.replace("\n", " | ")
    
    ShortSent = property(_get_short_sent)
    
    ShortReceived = property(_get_short_received)
    
    def __str__(self):
        return "%s) SENT: %s | RECV: %s" % (self.mTime, self.mSent, self.mRecv)
   
   
   
    
import unittest

class TestLogEntry(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def testshuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

    def testchoice(self):
        element = random.choice(self.seq)
        self.assert_(element in self.seq)

    def testsample(self):
        self.assertRaises(ValueError, random.sample, self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assert_(element in self.seq)

if __name__ == '__main__':
    unittest.main()
