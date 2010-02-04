
import time

connect("127.0.0.1", "10039", "weblab")

#test_me("hello")

start_experiment()

send_file("script.py", "A script file")

response = send_command("Test Command")

print "The response is: %s" % response 

msg_box("Test Message", "test")

time.sleep(2)

dispose()

disconnect()
