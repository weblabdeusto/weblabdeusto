import time
import json
import visir_commands
import traceback


from voodoo.representable import Representable

from weblab.core.reservations import Reservation
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.data.command import Command
from weblab.data.experiments import ExperimentId


VISIR_EXPERIMENT = "lxi_visir"
DEBUG = True
IGNORE_ASSERTIONS = True


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
            reservation = weblab.reserve_experiment(session_id, ExperimentId(VISIR_EXPERIMENT, "Visir experiments"), "{}", "{}")

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

            iteration = 0
            
            for _ in xrange(self.executions):
                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_11k % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                ar1 = AssertionResult(11000.0, 11000.0 * 0.2, result)
                if DEBUG and ar1.failed:
                    print "[Failed at 1st]" + str(ar1)
                if not IGNORE_ASSERTIONS: 
                    assertions.append(ar1)
                times.append(after - before)

# This command is currently commented out because it does not seem to be compatible with lxi_visir.
#                before = time.time()
#                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_rectifier % visir_sessionid))
#                after = time.time()
#                # Don't know how to measure the response, but at least check that the response is a valid VISIR response
#                result = visir_commands.parse_command_response(response, 'dmm_resolution')
#                assertions.append(AssertionResult(3.5, 200, result))
#                times.append(after - before)

                time.sleep(1)

                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_900 % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                ar3 = AssertionResult(900.0, 900.0 * 0.2, result)
                if DEBUG and ar3.failed:
                    print "[Failed at 3rd]" + str(ar3)
                if not IGNORE_ASSERTIONS:
                    assertions.append(ar3)
                times.append(after - before)

                time.sleep(1)

                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_1k % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                ar4 = AssertionResult(1000.0, 1000 * 0.2, result)
                if DEBUG and ar4.failed:
                    print "[Failed at 4th]" + str(ar4)
                if not IGNORE_ASSERTIONS:
                    assertions.append(ar4)
                times.append(after - before)

                time.sleep(1)

                before = time.time()
                response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_10k % visir_sessionid))
                after = time.time()
                result = visir_commands.parse_command_response(response)
                ar5 = AssertionResult(10000.0, 10000 * 0.2, result)
                if DEBUG and ar5.failed:
                    print "[Failed at 5th]" + str(ar5)
                if not IGNORE_ASSERTIONS:
                    assertions.append(ar5)
                times.append(after - before)
                
                iteration += 1
                
                time.sleep(1)

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
    USERNAME = "tester"
    PASSWORD = "t3st3r6"
    EXECUTIONS = 20
    tester = Tester(URL, USERNAME, PASSWORD, EXECUTIONS)
    result = tester.run()
    print result.failed

