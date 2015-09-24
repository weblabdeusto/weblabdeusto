from __future__ import print_function, unicode_literals
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import urllib2

class RequestSerializer(object):

    def generate_cancel(self, identifier, passkey, experiment_id):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <Cancel xmlns="http://ilab.mit.edu">
      <experimentID>%(experiment_id)s</experimentID>
    </Cancel>
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
            'experiment_id'            : escape(str(experiment_id)),
        }

    def generate_get_effective_queue_length(self, identifier, passkey, user_group, priority_hint):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <GetEffectiveQueueLength xmlns="http://ilab.mit.edu">
      <userGroup>%(user_group)s</userGroup>
      <priorityHint>%(priority_hint)s</priorityHint>
    </GetEffectiveQueueLength>
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
            'user_group'               : escape(str(user_group)),
            'priority_hint'            : escape(str(priority_hint)),
        }

    def generate_get_experiment_status(self, identifier, passkey, experiment_id):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <GetExperimentStatus xmlns="http://ilab.mit.edu">
      <experimentID>%(experiment_id)s</experimentID>
    </GetExperimentStatus>
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
            'experiment_id'            : escape(str(experiment_id)),
        }

    def generate_get_lab_configuration(self, identifier, passkey):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <GetLabConfiguration xmlns="http://ilab.mit.edu">
      <userGroup>WebLab-Deusto</userGroup>
    </GetLabConfiguration>
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
        }

    def generate_get_lab_info(self, identifier, passkey):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <GetLabInfo xmlns="http://ilab.mit.edu" />
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
        }

    def generate_get_lab_status(self, identifier, passkey):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <GetLabStatus xmlns="http://ilab.mit.edu" />
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
        }

    def generate_retrieve_result(self, identifier, passkey, experiment_id):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <RetrieveResult xmlns="http://ilab.mit.edu">
      <experimentID>%(experiment_id)s</experimentID>
    </RetrieveResult>
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
            'experiment_id'            : escape(str(experiment_id)),
        }

    def generate_submit(self, identifier, passkey, experiment_id, experiment_specification, user_group, priority_hint):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <Submit xmlns="http://ilab.mit.edu">
      <experimentID>%(experiment_id)s</experimentID>
      <experimentSpecification>%(experiment_specification)s</experimentSpecification>
      <userGroup>%(user_group)s</userGroup>
      <priorityHint>%(priority_hint)s</priorityHint>
    </Submit>
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
            'experiment_id'            : escape(str(experiment_id)),
            'experiment_specification' : escape(str(experiment_specification)),
            'user_group'               : escape(str(user_group)),
            'priority_hint'            : escape(str(priority_hint)),
        }

    def generate_validate(self, identifier, passkey, experiment_specification, user_group):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthHeader xmlns="http://ilab.mit.edu">
      <identifier>%(identifier)s</identifier>
      <passKey>%(passkey)s</passKey>
    </AuthHeader>
  </soap:Header>
  <soap:Body>
    <Validate xmlns="http://ilab.mit.edu">
      <experimentSpecification>%(experiment_specification)s</experimentSpecification>
      <userGroup>%(user_group)s</userGroup>
    </Validate>
  </soap:Body>
</soap:Envelope>""" % {
            'identifier'               : escape(str(identifier)),
            'passkey'                  : escape(str(passkey)),
            'experiment_specification' : escape(str(experiment_specification)),
            'user_group'               : escape(str(user_group)),
        }

    def generate_submit_response(self, accepted, estimated_runtime, experiment_id, min_time, effective_queue_length, estimated_wait):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<SubmitResponse xmlns="http://ilab.mit.edu">
<SubmitResult>
<vReport>
<accepted>%(accepted)s</accepted>
<errorMessage />
<estRuntime>%(est_rt)s</estRuntime>
</vReport>
<experimentID>%(experiment_id)s</experimentID>
<minTimeToLive>%(min_time)s</minTimeToLive>
<wait>
<effectiveQueueLength>%(effective_queue_length)s</effectiveQueueLength>
<estWait>%(estimated_wait)s</estWait>
</wait>
</SubmitResult>
</SubmitResponse>
</soap:Body>
</soap:Envelope>""" % {
            'accepted'                  : escape(str(accepted).lower()),
            'est_rt'                    : escape(str(estimated_runtime)),
            'experiment_id'             : escape(str(experiment_id)),
            'min_time'                  : escape(str(min_time)),
            'effective_queue_length'    : escape(str(effective_queue_length)),
            'estimated_wait'            : escape(str(estimated_wait))
        }

    def generate_lab_configuration_response(self, configuration):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<GetLabConfigurationResponse xmlns="http://ilab.mit.edu">
<GetLabConfigurationResult>%s</GetLabConfigurationResult></GetLabConfigurationResponse>
</soap:Body>
</soap:Envelope>""" % escape(configuration)

    def generate_get_experiment_status_response(self, status, effective_queue_length, estimated_wait, estimated_runtime, estimated_remaining_runtime, min_time_to_live):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<GetExperimentStatusResponse xmlns="http://ilab.mit.edu">
<GetExperimentStatusResult>
<statusReport>
<statusCode>%(status)s</statusCode>
<wait>
<effectiveQueueLength>%(effective_queue_length)s</effectiveQueueLength>
<estWait>%(estimated_wait)s</estWait>
</wait>
<estRuntime>%(estimated_runtime)s</estRuntime>
<estRemainingRuntime>%(estimated_remaining_runtime)s</estRemainingRuntime>
</statusReport>
<minTimetoLive>%(min_time_to_live)s</minTimetoLive>
</GetExperimentStatusResult>
</GetExperimentStatusResponse>
</soap:Body>
</soap:Envelope>""" % {
            'status'                      : escape(str(status)),
            'effective_queue_length'      : escape(str(effective_queue_length)),
            'estimated_wait'              : escape(str(estimated_wait)),
            'estimated_runtime'           : escape(str(estimated_runtime)),
            'estimated_remaining_runtime' : escape(str(estimated_remaining_runtime)),
            'min_time_to_live'            : escape(str(min_time_to_live)),
        }

    def generate_retrieve_result_response(self, status, result, resultext):
        return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body>
<RetrieveResultResponse xmlns="http://ilab.mit.edu">
<RetrieveResultResult>
<statusCode>%(status)s</statusCode>
<experimentResults>%(result)s</experimentResults>
<xmlResultExtension>%(resultext)s</xmlResultExtension>
<warningMessages>
<string />
</warningMessages>
<errorMessage />
</RetrieveResultResult>
</RetrieveResultResponse>
</soap:Body>
</soap:Envelope>""" % {
                'status'                 : escape(str(status)),
                'result'                 : escape(str(result)),
                'resultext'              : escape(str(resultext)),
        }

    def _load(self, payload):
        return ET.ElementTree(ET.fromstring(payload))

    def parse_cancel_response(self, payload):
        tree = self._load(payload)
        return tree.find("./*/{http://ilab.mit.edu}CancelResponse/{http://ilab.mit.edu}CancelResult").text == 'true'

    def parse_get_effective_queue_length_response(self, payload):
        tree = self._load(payload)
        length = int(tree.find("./*/{http://ilab.mit.edu}GetEffectiveQueueLengthResponse/{http://ilab.mit.edu}GetEffectiveQueueLengthResult/{http://ilab.mit.edu}effectiveQueueLength").text)
        wait = float(tree.find("./*/{http://ilab.mit.edu}GetEffectiveQueueLengthResponse/{http://ilab.mit.edu}GetEffectiveQueueLengthResult/{http://ilab.mit.edu}estWait").text)
        return length, wait

    def parse_get_experiment_status_response(self, payload):
        tree = self._load(payload)
        result = tree.find("./*/{http://ilab.mit.edu}GetExperimentStatusResponse/{http://ilab.mit.edu}GetExperimentStatusResult")
        code = int(result.find("./{http://ilab.mit.edu}statusReport/{http://ilab.mit.edu}statusCode").text)
        length = int(result.find("./{http://ilab.mit.edu}statusReport/{http://ilab.mit.edu}wait/{http://ilab.mit.edu}effectiveQueueLength").text)
        #estWait = float(result.find("./{http://ilab.mit.edu}statusReport/{http://ilab.mit.edu}wait/{http://ilab.mit.edu}estWait").text)
        estWait = None
        #estRt = float(result.find("./{http://ilab.mit.edu}statusReport/{http://ilab.mit.edu}estRuntime").text)
        estRt = None
        #estRemRt = float(result.find("./{http://ilab.mit.edu}statusReport/{http://ilab.mit.edu}estRemainingRuntime").text)
        estRemRt = None
        #minToLive = float(result.find("./{http://ilab.mit.edu}minTimetoLive").text)
        minToLive = None
        return code, length, estWait, estRt, estRemRt, minToLive

    def parse_get_lab_configuration_response(self, payload):
        tree = self._load(payload)
        return tree.find("./*/{http://ilab.mit.edu}GetLabConfigurationResponse/{http://ilab.mit.edu}GetLabConfigurationResult").text

    def parse_get_lab_info_response(self, payload):
        tree = self._load(payload)
        return tree.find("./*/{http://ilab.mit.edu}GetLabInfoResponse/{http://ilab.mit.edu}GetLabInfoResult").text

    def parse_get_lab_status_response(self, payload):
        tree = self._load(payload)
        online = tree.find("./*/{http://ilab.mit.edu}GetLabStatusResponse/{http://ilab.mit.edu}GetLabStatusResult/{http://ilab.mit.edu}online").text == 'true'
        message = tree.find("./*/{http://ilab.mit.edu}GetLabStatusResponse/{http://ilab.mit.edu}GetLabStatusResult/{http://ilab.mit.edu}labStatusMessage").text
        return online, message

    def parse_retrieve_results_response(self, payload):
        tree = self._load(payload)
        result   = tree.find("./*/{http://ilab.mit.edu}RetrieveResultResponse/{http://ilab.mit.edu}RetrieveResultResult")
        code     = int(result.find("./{http://ilab.mit.edu}statusCode").text)
        results  = result.find("./{http://ilab.mit.edu}experimentResults").text
        xmlResultExtension = result.find("./{http://ilab.mit.edu}xmlResultExtension").text
        #xmlBlobExtension   = result.find("./{http://ilab.mit.edu}xmlBlobExtension").text
        xmlBlobExtension   = None
        # warnings           = result.find("./{http://ilab.mit.edu}warningMessages")
        warnings           = None
        # error              = result.find("./{http://ilab.mit.edu}errorMessage").text
        error              = None
        return code, results, xmlResultExtension, xmlBlobExtension, warnings, error

    def parse_submit_response(self, payload):
        tree = self._load(payload)
        result     = tree.find("./*/{http://ilab.mit.edu}SubmitResponse/{http://ilab.mit.edu}SubmitResult")
        #accepted   = result.find("./{http://ilab.mit.edu}vReport/{http://ilab.mit.edu}accepted").text == 'true'
        accepted   = None
        warnings   = None
        #error      = result.find("./{http://ilab.mit.edu}vReport/{http://ilab.mit.edu}errorMessage").text
        error      = None
        #estRuntime = float(result.find("./{http://ilab.mit.edu}vReport/{http://ilab.mit.edu}estRuntime").text)
        estRuntime  = None

        #labExpId      = int(result.find("./{http://ilab.mit.edu}labExperimentID").text)
        labExpId      = None
        #minTimetoLive = float(result.find("./{http://ilab.mit.edu}minTimetoLive").text)
        minTimetoLive = None
        
        queue_length_node = result.find("./{http://ilab.mit.edu}wait/{http://ilab.mit.edu}effectiveQueueLength")
        if queue_length_node is not None:
            queue_length = int(result.find("./{http://ilab.mit.edu}wait/{http://ilab.mit.edu}effectiveQueueLength").text)
        else:
            queue_length = 1
        #wait         = float(result.find("./{http://ilab.mit.edu}wait/{http://ilab.mit.edu}estWait").text)
        wait         = None

        return accepted, warnings, error, estRuntime, labExpId, minTimetoLive, queue_length, wait

    def parse_validate_response(self, payload):
        tree = self._load(payload)
        result     = tree.find("./*/{http://ilab.mit.edu}ValidateResponse/{http://ilab.mit.edu}ValidateResult")
        accepted   = result.find("./{http://ilab.mit.edu}accepted").text == 'true'
        warnings   = None
        error      = result.find("./{http://ilab.mit.edu}errorMessage").text
        estRuntime = float(result.find("./{http://ilab.mit.edu}estRuntime").text)

        return accepted, warnings, error, estRuntime

    def parse_get_lab_configuration_request(self, payload):
        tree = self._load(payload)
        return tree.find("./*/{http://ilab.mit.edu}GetLabConfiguration/{http://ilab.mit.edu}labServerID").text

    def parse_submit_request(self, payload):
        tree = self._load(payload)
        submit = tree.find("./*/{http://ilab.mit.edu}Submit")
        lab_server_id           = submit.find("./{http://ilab.mit.edu}labServerID").text
        experimentSpecification = submit.find("./{http://ilab.mit.edu}experimentSpecification").text
        priorityHint            = int(submit.find("./{http://ilab.mit.edu}priorityHint").text)
        emailNotification       = submit.find("./{http://ilab.mit.edu}emailNotification").text == 'true'
        return lab_server_id, experimentSpecification, priorityHint, emailNotification

    def parse_get_experiment_status_request(self, payload):
        tree = self._load(payload)
        experiment_status = tree.find("./*/{http://ilab.mit.edu}GetExperimentStatus")
        return int(experiment_status.find("./{http://ilab.mit.edu}experimentID").text)

    def parse_retrieve_result_request(self, payload):
        tree = self._load(payload)
        experiment_status = tree.find("./*/{http://ilab.mit.edu}RetrieveResult")
        return int(experiment_status.find("./{http://ilab.mit.edu}experimentID").text)

class iLabBatchLabServerProxy(object):
    def __init__(self, url, identifier, passkey):
        self.url        = url
        self.identifier = identifier
        self.passkey    = passkey
        self.serializer = RequestSerializer()

    def _call(self, request_data, soapaction):
        request = urllib2.Request(self.url, request_data, {'SOAPAction' : soapaction, 'Content-Type' : 'text/xml' })
        return urllib2.urlopen(request).read()

    def get_lab_configuration(self):
        request_data = self.serializer.generate_get_lab_configuration(self.identifier, self.passkey)
        soapaction   = '"http://ilab.mit.edu/GetLabConfiguration"'
        response = self._call(request_data, soapaction)
        return self.serializer.parse_get_lab_configuration_response(response)

    def submit(self, experiment_id, experiment_specification, user_group, priority_hint):
        request_data =self.serializer.generate_submit(self.identifier, self.passkey, experiment_id, experiment_specification, user_group, priority_hint)
        soapaction   = '"http://ilab.mit.edu/Submit"'
        response    = self._call(request_data, soapaction)
        return self.serializer.parse_submit_response(response)

    def get_experiment_status(self, experiment_id):
        request_data = self.serializer.generate_get_experiment_status(self.identifier, self.passkey, experiment_id)
        soapaction   = '"http://ilab.mit.edu/GetExperimentStatus"'
        response     = self._call(request_data, soapaction)
        return self.serializer.parse_get_experiment_status_response(response)

    def retrieve_result(self, experiment_id):
        request_data = self.serializer.generate_retrieve_result(self.identifier, self.passkey, experiment_id)
        soapaction   = '"http://ilab.mit.edu/RetrieveResult"'
        response     = self._call(request_data, soapaction)
        return self.serializer.parse_retrieve_results_response(response)

    def cancel(self, experiment_id):
        request_data = self.serializer.generate_cancel(self.identifier, self.passkey, experiment_id)
        soapaction   = '"http://ilab.mit.edu/Cancel"'
        self._call(request_data, soapaction)

