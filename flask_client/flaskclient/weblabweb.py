import json
import requests


# TODO: Make this dynamic.
BASE_URL = "https://www.weblab.deusto.es/weblab"


class WeblabWebException(Exception):
    pass


class WeblabWeb(object):
    """
    Port of the weblabweb.js script to Python.
    """

    def __init__(self):
        pass

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
        result = requests.post(target_url, data=json.dumps(request), headers={"content-type": "application/json"})
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

        @param {str} account: Accoun tname.
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

