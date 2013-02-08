import time
import json
import visir_commands
import traceback


from voodoo.representable import Representable

from weblab.core.reservations import Reservation
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.data.command import Command
from weblab.data.experiments import ExperimentId


class AssertionResult(object):

    __metaclass__ = Representable

    def __init__(self, expected, expected_delta, returned):
        self.expected       = expected
        self.expected_delta = expected_delta
        self.returned       = returned
        self.failed         = abs(expected - returned) > expected_delta

class TesterResult(object):

    __metaclass__ = Representable

    def __init__(self, failed, assertions, exception, times):
        self.failed      = failed
        self.assertions  = assertions
        self.exception   = exception
        self.times       = times

class Tester(object):
    def __init__(self, url, username, password, executions):
        self.url      = url
        self.username = username
        self.password = password
        self.executions = executions

    def run(self):
        assertions  = []
        times       = []
        print "Starting process"

        reservation_id = None

        try:
            weblab      = WebLabDeustoClient(self.url)
            session_id  = weblab.login(self.username, self.password)
            reservation = weblab.reserve_experiment(session_id, ExperimentId("visir", "Visir experiments"), "{}", "{}")

            while reservation.status in (Reservation.WAITING_CONFIRMATION or Reservation.WAITING):
                time.sleep(1)
                reservation = weblab.get_reservation_status( reservation.reservation_id )

            if reservation.status != Reservation.CONFIRMED:
                raise Exception("Confirmed reservation expected for reservation_id (%r). Found status: %r" % (reservation.reservation_id, reservation.status))

            print "Confirmed reservation, starting..."

            reservation_id = reservation.reservation_id
            initial_config = reservation.initial_configuration

            cookie   = json.loads(initial_config)['cookie']

            login_response = weblab.send_command(reservation_id, Command(visir_commands.visir_login_request % cookie))

            visir_sessionid = visir_commands.parse_login_response(login_response)

            for _ in xrange(self.executions):
                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_11k % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                assertions.append(AssertionResult(11000.0, 200, result))
                times.append(after - before)

                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_rectifier % visir_sessionid))
                after = time.time()
                # Don't know how to measure the response, but at least check that the response is a valid VISIR response
                result = visir_commands.parse_command_response(response, 'dmm_resolution')
                assertions.append(AssertionResult(3.5, 200, result))
                times.append(after - before)

                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_900 % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                assertions.append(AssertionResult(900.0, 200, result))
                times.append(after - before)

                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_1k % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                assertions.append(AssertionResult(1000.0, 200, result))
                times.append(after - before)


                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_10k % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                assertions.append(AssertionResult(10000.0, 200, result))
                times.append(after - before)

            weblab.finished_experiment(reservation_id)
        except Exception as exception:
            if reservation_id is not None:
                try:
                    weblab.finished_experiment(reservation_id)
                    loggedout = True
                except:
                    loggedout = False
            else:
                loggedout = "no id provided"
            print "Finished with exception and logged out: %s" % loggedout
            traceback.print_exc()

            return TesterResult(True, assertions, exception, times)
        else:
            print "Finished without exception"
            return TesterResult(any(map(lambda assertion : assertion.failed, assertions)), assertions, None, times)
    
        
if __name__ == '__main__':
    URL = "http://www.weblab.deusto.es/weblab/"
    USERNAME = "demo"
    PASSWORD = "demo"
    EXECUTIONS = 2
    tester = Tester(URL, USERNAME, PASSWORD, EXECUTIONS)
    result = tester.run()

