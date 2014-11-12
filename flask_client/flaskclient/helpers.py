import re
import requests
from . import flask_app


def _retrieve_configuration_js():
    """
    Returns the configuration JS. This is mostly for the configuration function, but
    also so that it can be used from outside. This will eventually be removed altogether
    when the configuration.js file disappears.

    @see configuration
    @rtype str
    """
    config = requests.get(flask_app.config["LAB_URL"] + "configuration.js")
    js = config.content

    def remove_comments(string):
        """
        Removes comments from a string, supports // and /* formats. From Stack Overflow.
        @param str string: Original text.
        @return: Text without comments.
        @rtype: str
        """
        pattern = r"((?<!\\)\".*?(?<!\\)\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
        # first group captures quoted strings (double or single)
        # second group captures comments (//single-line or /* multi-line */)
        regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

        def _replacer(match):
            # if the 2nd group (capturing comments) is not None,
            # it means we have captured a non-quoted (real) comment string.
            if match.group(2) is not None:
                return ""  # so we will return empty to remove the comment
            else:  # otherwise, we will return the 1st group
                return match.group(1)  # captured quoted-string

        return regex.sub(_replacer, string)

    js = remove_comments(js)

    return js