import json
import requests


# TODO: Make this dynamic.
BASE_URL = "https://www.weblab.deusto.es/weblab"


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
        @returns str The sessionid.
        """
        req = {
            "method": "login",
            "params": {
                "username": account,
                "password": password
            }
        }

        result = self._send(BASE_URL + "/login/json/", req)
        return result["id"]

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

        result = self._send(BASE_URL + "/json/", req)
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

        result = self._send(BASE_URL + "/json/", req)
        return result

