import re


def remove_comments_from_json(string):
    """
    Removes comments from a JSON string, supports // and /* formats. From Stack Overflow.
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




# # Redirection utils from Flask manual / pocoo.
# # http://flask.pocoo.org/snippets/62/
#
# def is_safe_url(target):
#     """
#     Checks if an URL is safe for redirection via URL.
#     # TODO: Reportedly by some comments not a safe check.
#     :param target:
#     :return:
#     """
#     ref_url = urlparse(request.host_url)
#     test_url = urlparse(urljoin(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and \
#            ref_url.netloc == test_url.netloc
#
#
# def get_redirect_target():
#     """
#     Find out where we need to redirect.
#     :return:
#     """
#     for target in request.values.get('next'), request.referrer:
#         if not target:
#             continue
#         if is_safe_url(target):
#             return target
#
# def redirect_back(endpoint, **values):
#     target = request.form['next']
#     if not target or not is_safe_url(target):
#         target = url_for(endpoint, **values)
#     return redirect(target)
#
#
#
#
#
#