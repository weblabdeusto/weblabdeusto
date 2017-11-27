from __future__ import print_function, unicode_literals
from babel import Locale, UnknownLocaleError
from flask import request, session
import traceback

try:
    USE_BABELEX = True

    if USE_BABELEX:
        # Use regular Babelex instead of Babel
        from flask.ext.babelex import Babel as Babel_ex, gettext as gettext_ex, lazy_gettext as lazy_gettext_ex, ngettext as ngettext_ex, get_locale as get_locale_ex

        gettext = gettext_ex
        ngettext = ngettext_ex
        lazy_gettext = lazy_gettext_ex
        get_locale = get_locale_ex
        Babel = Babel_ex
    else:
        # Use regular Babel instead of Babelex
        from flask.ext.babel import Babel as Babel_reg, gettext as gettext_reg, lazy_gettext as lazy_gettext_reg, ngettext as ngettext_reg, get_locale as get_locale_reg

        gettext = gettext_reg
        ngettext = ngettext_reg
        lazy_gettext = lazy_gettext_reg
        get_locale = get_locale_reg
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

    def get_locale():
        return 'en'


def initialize_i18n(app):
    if Babel is None:
        print("Not using Babel. Everything will be in English")
    else:
        babel = Babel(app)

        supported_languages = ['en']
        supported_languages.extend([translation.language for translation in babel.list_translations()])

        def check_locale(locale):
            if locale:
                try:
                    Locale.parse(locale)
                except ValueError:
                    return None
                except UnknownLocaleError:
                    return None
                except Exception:
                    traceback.print_exc()
                    return None
                else:
                    return locale
            return None

        @babel.localeselector
        def get_locale():
            locale = check_locale(request.args.get('locale', None))
            if locale is None:
                locale = check_locale(session.get('locale', None))
            if locale is None:
                locale = request.accept_languages.best_match(supported_languages)
            if locale is None:
                locale = 'en'
            session['locale'] = locale
            return locale
        return babel
