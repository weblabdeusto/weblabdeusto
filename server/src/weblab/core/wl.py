from weblab.core.new_server import WebLabAPI

weblab_api = WebLabAPI(['login_web', 'web', 'webclient'])


import webclient.web as web
assert web is not None

@weblab_api.route_webclient("/test/", methods=["GET", "POST"])
def test():
    weblab_api.ctx.reservation_id = "TEST"
    return "HAI"


