from mdt69x import Controller

# Empty initializer cycles through all ports to find the first port that responds like a MTD69x
controller = Controller()
# or, if you know the port name: controller = Controller("COM1")
# Specifying the port name lead to a faster connection

controller.get_id()  # This will print some info about the controller
# controller.get_available_commands()  # This will print all available commands. Might be quite a few!
print("")

limit = controller.get_switch_limit()
print("Selected voltage limit: %.4f V" % limit)

x_volt = controller.get_x_voltage()
print("X volt: %.4f V" % x_volt)

# Another way.
# This uses non-compatible commands and might give more accurate results
# (2 decimal digits instead of one of the command above)
x, y, z = controller.get_xyz_voltage()
print("X: %.4f V Y: %.4f V Z: %.4f V" % (x, y, z))

controller.set_x_voltage(50.0)
# or:
controller.set_xyz_voltage(50.0, y, z)

# Close the connection
controller.close()