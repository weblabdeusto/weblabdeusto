from weblab.core.new_server import WebLabAPI

weblab_api = WebLabAPI(['login_web', 'web', 'webclient'])

@weblab_api.route_webclient("/test/", methods=["GET", "POST"])
def test():
    weblab_api.ctx.reservation_id = "TEST"
    return "HAI"


