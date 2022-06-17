from mdt69x import Controller

#device 1
controller1 = Controller("COM3")
controller1.get_id()

#device 2
controller2 = Controller("COM9")
controller2.get_id()


controller1.get_id()
controller2.get_id()
print("")

# Close the connection
controller1.close()
controller2.close()