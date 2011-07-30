from urllib import addinfourl
from cStringIO import StringIO

class fakeaddinfourl(addinfourl):
  def __init__(self, response='', headers={}, url=''):
    if isinstance(response, basestring):
      response = StringIO(response)
    addinfourl.__init__(self, response, headers, url)