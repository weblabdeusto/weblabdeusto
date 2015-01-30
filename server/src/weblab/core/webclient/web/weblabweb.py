import json
import requests


class WeblabWebException(Exception):
    pass


class WeblabWeb(object):
    """
    Port of the weblabweb.js script to Python.
    Each instance of WeblabWeb should only be used with a single user, because the internally-kept session
    stores cookies, which are required due to Weblab's load distribution scheme.
    """

    def __init__(self):
        self.s = requests.Session()
        self.core_url = None
        self.login_url = None
        self.set_target_urls_to_standard()

    def set_target_urls(self, login_url, core_url):
        """
        Sets the URLs to which the AJAX requests will be directed.
        @param {str} login_url: URL of the login server (used for the login request)
        @param {str} core_url: URL of the core server (used for most requests)

        Note that by default requests will be directed to the standard Weblab instance,
        that is, to the Weblab instance located at //www.weblab.deusto.es/weblab. These
        can also be explicitly reset through setTargetURLsToStandard.
        @see set_target_urls_to_standard

        Note also that testing target URLs (for use with launch_samples.py or with the
        test script which relies on it) can also be set easily through setTargetURLsToTesting.
        @see set_target_urls_to_testing
        """
        self.core_url = core_url
        self.login_url = login_url

    def set_target_urls_to_standard(self):
        """
        Sets the target URLs to the standard ones. That is, the ones that will work
        on the main Weblab instance, which is at //www.weblab.deusto.es.
        # TODO: Consider changing them to HTTPs.
        """
        self.login_url = "http://www.weblab.deusto.es/weblab/login/json/"
        self.core_url = "http://www.weblab.deusto.es/weblab/json/"

    def set_target_urls_to_testing(self):
        """
        SEts the target urls to the ones that can be used for local automated testing. That is,
        the ones that will work with a local Weblab instance started through the launch_sample
        configuration, which is the one typically used for development.
        """
        self.login_url = "http://localhost:18645/"
        self.core_url = "http://localhost:18345/"

    def _feed_cookies(self, cookies):
        """
        Updates the internal dictionary of cookies with the provided cookies.
        This has been added to solve the routing issue and basically to try to
        re-send all client cookies.
        TODO: Modify this scheme, which is way too weird and potentially buggy.
        """
        self.s.cookies.update(cookies)

    def _send(self, target_url, request):
        """
        Internal send function. It will send the request to the target URL.
        Meant only for internal use. If an error occurs (network error, "is_exception" to true, or other) then
        the exception will be printed to console, and nothing else will happen (as of now).

        @param {str} target_url: The target URL.
        @param {object} request: The JSON-able to send. This method will not check whether the format of the JSON-able is
        right or not. It is assumed it is. This should be a JSON-able object and NOT a JSON string.

        @returns {object} JSON result
        """

        result = self.s.post(target_url, data=json.dumps(request), headers={"content-type": "application/json"})
        """ @type: requests.Response """

        if result.status_code != 200:
            raise WeblabWebException(request)

        response = result.json()
        if "is_exception" not in response or response["is_exception"]:
            raise WeblabWebException(response)

        if "result" not in response:
            raise WeblabWebException(response)

        return response["result"]

    def _login(self, account, password):
        """
        Login to the server.

        @param {str} account: Account name.
        @param {str} password: Password.
        @returns {(str, str)} The sessionid and route.
        """
        req = {
            "method": "login",
            "params": {
                "username": account,
                "password": password
            }
        }

        result = self._send(self.login_url, req)

        sid, route = result["id"], self.s.cookies.get("weblabsessionid").split(".")[1]

        return sid, route

    def _logout(self, sessionid):
        """
        Logs the user out.

        @param {str} sessionid: Sessionid of the user to logout
        @returns {None} None
        """
        req = {
            "method": "logout",
            "params": {
                "session_id": {"id": sessionid}
            }
        }

        result = self._send(self.core_url, req)
        return None

    def _get_user_information(self, sessionid):
        """
        Retrieves the user information that the server relates to
        the specified session ID.

        @param {str} sessionid: Sessionid of the user
        @returns object User information
        """
        req = {
            "method": "get_user_information",
            "params": {
                "session_id": {"id": sessionid}
            }
        }

        result = self._send(self.core_url, req)
        return result

    def _list_experiments(self, sessionid):
        """
        Lists available experiments for the user.

        @param {str} sessionid: Sessionid of the user
        @returns object List of experiments
        """
        req = {
            "method": "list_experiments",
            "params": {
                "session_id": {"id": sessionid}
            }
        }

        result = self._send(self.core_url, req)
        return result

