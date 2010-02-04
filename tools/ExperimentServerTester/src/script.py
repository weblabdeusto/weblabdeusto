


connect("127.0.0.1", "5678", "weblab")

#test_me("hello")

start_experiment()

send_file("script.py", "A script file")

send_command("Test Command")

msg_box("Test Message", "test")

dispose()

disconnect()
