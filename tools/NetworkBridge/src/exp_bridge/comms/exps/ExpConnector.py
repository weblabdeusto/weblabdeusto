import gevent


class ExpConnector(object):
    """
    Class that will periodically check whether a local ExperimentServer has become available, and if so, will
    establish a connection and mark it as available.
    """

    def __init__(self, exp_name, exp_server_host, exp_server_port, exp_server_path):
        super(ExpConnector, self).__init__()
        self.exp_name = exp_name
        self.exp_server_host = exp_server_host
        self.exp_server_port = exp_server_port
        self.exp_server_path = exp_server_path
        self._should_stop = False

        print "Initializing the ExpConnector client"

    def start(self):
        """
        Starts the greenlet that will keep trying to connect to the specified local Experiment Server.
        :return:
        """
        self._greenlet = gevent.spawn(self.run)

    def run(self):
        while not self._should_stop:
            print "On ExpConnector run()"
            gevent.sleep(1)

    def stop(self):
        """
        Stops the greenlet that will keep trying to connect to the specified local Experiment Server.
        :return:
        """
        self._should_stop = True
