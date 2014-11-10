import traceback

try:
    USE_BABELEX = True

    if USE_BABELEX:
        # Use regular Babelex instead of Babel
        from flask.ext.babelex import Babel as Babel_ex, gettext as gettext_ex, lazy_gettext as lazy_gettext_ex, ngettext as ngettext_ex

        gettext = gettext_ex
        ngettext = ngettext_ex
        lazy_gettext = lazy_gettext_ex
        Babel = Babel_ex
    else:
        # Use regular Babel instead of Babelex
        from flask.ext.babel import Babel as Babel_reg, gettext as gettext_reg, lazy_gettext as lazy_gettext_reg, ngettext as ngettext_reg

        gettext = gettext_reg
        ngettext = ngettext_reg
        lazy_gettext = lazy_gettext_reg
        Babel = Babel_reg

except ImportError:

    DEBUG = True
    if DEBUG:
        traceback.print_exc()

    Babel = None

    def gettext(string, **variables):
        return string % variables

    def ngettext(singular, plural, num, **variables):
        return (singular if num == 1 else plural) % variables

    def lazy_gettext(string, **variables):
        return gettext(string, **variables)

