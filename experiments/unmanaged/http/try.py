import json
import requests

# To try whether a server is working.



target = "http://localhost:5000/sample/weblab/sessions/"
headers = {"content-type": "application/json"}

#req = """{"client_initial_data":"{\"back\": \"http://localhost/weblab/client/index.html#page=experiment&exp.category=HTTP%20experiments&exp.name=http\"}","server_initial_data":"{\"request.locale\": \"\", \"request.experiment_id.experiment_name\": \"http\", \"request.experiment_id.category_name\": \"HTTP experiments\", \"priority.queue.slot.initialization_in_accounting\": true, \"priority.queue.slot.start\": \"2014-10-03 16:29:40.895892\", \"priority.queue.slot.length\": \"200.0\", \"request.username\": \"any\", \"request.full_name\": \"any\"}","back":"http://localhost/weblab/client/index.html#page=experiment&exp.category=HTTP%20experiments&exp.name=http"}"""
req = """{"client_initial_data":"{\\"back\\": \\"http://localhost/weblab/client/index.html#page=experiment&exp.category=HTTP%20experiments&exp.name=http\\"}","server_initial_data":"{\\"request.locale\\": \\"\\", \\"request.experiment_id.experiment_name\\": \\"http\\", \\"request.experiment_id.category_name\\": \\"HTTP experiments\\", \\"priority.queue.slot.initialization_in_accounting\\": true, \\"priority.queue.slot.start\\": \\"2014-10-03 16:54:02.394173\\", \\"priority.queue.slot.length\\": \\"200.0\\", \\"request.username\\": \\"any\\", \\"request.full_name\\": \\"any\\"}","back":"http://localhost/weblab/client/index.html#page=experiment&exp.category=HTTP%20experiments&exp.name=http"}"""

j = json.loads(req)
r = requests.post(target, data=json.dumps(j), headers=headers)

print r.status_code

print r.content

