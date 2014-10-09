import os

from staticjinja import Renderer
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-s", "--dont-stop", dest="dont_stop",
                    help="Don't stop for reloading", action='store_true', default=False)
    (options, args) = parser.parse_args()

    def filter_func(filepath):
        filename = os.path.basename(filepath)
        if filename.startswith(('.', '_')):
            return False
        if not filename.endswith('.html'):
            return False
        return True

    def dont_render(*args, **kwargs):
        print "Rendering..."
        pass

    renderer = Renderer(outpath='./output', rules = [ ('.*.tmp', dont_render), ('.*.swx', dont_render) ])
    renderer.filter_func = filter_func
    renderer.run(debug=True, use_reloader = not options.dont_stop)
