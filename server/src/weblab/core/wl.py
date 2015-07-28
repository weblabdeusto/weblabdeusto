from __future__ import print_function, unicode_literals
from weblab.core.new_server import WebLabAPI

weblab_api = WebLabAPI(['login_web', 'web', 'webclient'])


import webclient as web
assert web is not None


