# Keeps track of the requests to forward.
import gevent

from gevent.queue import Queue

_exp_connectors = {}
""" :type: {str: expbridge.BaseConnector} """


class ExperimentNotFound(Exception):
    """
    To be raised when a connector for a specified experiment is not found.
    """
    pass


def _reset():
    """
    Clears the internal registry of connectors.
    :return:
    """
    global _exp_connectors
    _exp_connectors = {}


def forward_request(experiment, req):
    """
    Forwards a request through the appropriate connector, which must have been registered
    for the experiment beforehand. This will block until the response is available, so
    it should be called from a greenlet. It will throw an ExperimentNotFound exception
    is the appropriate connector does not seem to be available.

    :param experiment: Target experiment.
    :param req: Request data.
    :return: The response to the send_request request.
    """

    connector = _exp_connectors.get(experiment, None)
    """ :type : lab_bridge.comms.expbridge.BaseConnector.BaseConnector """

    if connector is None:
        raise ExperimentNotFound()

    response = connector.send_request(experiment, req)

    return response


def add_connector(exp, connector):
    """
    Registers a connector, which will handle the specific experiment. The same connector can handle
    several experiments, but this method will need to be called once for each of them.
    :param exp: Experiment to handle.
    :type exp: str
    :param connector: Connector which will handle that experiment.
    :type connector: lab_bridge.comms.expbridge.BaseConnector.BaseConnector
    :return:
    """
    _exp_connectors[exp] = connector
