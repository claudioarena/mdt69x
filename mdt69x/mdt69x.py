import serial
import sys
import glob

# Should work in both compatible or non compatible mode, but compatible mode should be faster

## Not implemented:

# DACSTEP?	Gets DAC step size used with up/down arrow keys. (1-5000).
# DACSTEP=	Sets DAC step size used with up/down arrow keys. (1-5000).
# Up Arrow	Increase selected channel by the set step size.
# Down Arrow	Decrease selected channel by the set step size.
# Right Arrow	Select next channel.
# Left Arrow	Select previous channel.

# Also, Echo on isn't implemented.
# Implementing it implies change to the code, to parse the echo response


class Controller:
    _ser = serial.Serial()
    _commands = ""
    _model = ""
    _firmaware_version = ""
    _voltage_range = ""
    _serial_number = ""
    _name = ""
    _compatible = 0
    _error_character = ''
    _master_scan_enabled = 0
    _voltage_commands_set = ["", "", "", ""]
    _voltage_commands_get = ["", "", ""]
    _voltage_max_commands_set = ["", "", "", ""]
    _voltage_min_commands_set = ["", "", "", ""]
    _voltage_max_commands_get = ["", "", "", ""]
    _voltage_min_commands_get = ["", "", "", ""]

    ECHO_OFF = 0
    ECHO_ON = 1
    COMPATIBILITY_OFF = 0
    COMPATIBILITY_ON = 1
    SUCCESS = 1
    FAIL = -1
    MASTER_SCAN_ON = 1
    MASTER_SCAN_OFF = 0
    PUSH_MODE_OFF = 0
    PUSH_MODE_ON = 1
    ROTARY_MODE_DEFAULT = 0
    ROTARY_MODE_TURN_POT = 1
    ROTARY_MODE_FINE = 2


    def __init__(self, port=""):
        self._ser.baudrate = 115200
        self._ser.bytesize = serial.EIGHTBITS
        self._ser.parity = serial.PARITY_NONE
        self._ser.stopbits = serial.STOPBITS_ONE
        self._ser.xonxoff = False
        self._ser.timeout = 1
        self._ser.write_timeout = 1
        self._ser.setDTR(False)
        self._ser.setRTS(False)

        if port is "":
            port = self._find_port()  # Check all ports

        elif self._check_port(port) is False:  # Check the provided port is correct
            raise OSError("Provided Serial port isn't correct")

        self._ser.port = port
        self._ser.close()  # In case it wasn't closed properly last time
        self._ser.open()
        self._ser.flushInput()
        self.set_echo_off()
        self.set_compatibility_on()

    def _check_port(self, port):
        try:
            self._ser.port = port
            self._ser.close()  # In case it wasn't closed properly last time
            self._ser.open()
            self._ser.flushInput()
            self._ser.write('\n\r'.encode('utf-8'))
            res = self._ser.read(100) # Read all characters available
            self._ser.close()
            if res == b'CMD_NOT_DEFINED>' or res == b'!' or res == b'\n\r!':
                return True
            else:
                return False
        except (OSError, serial.SerialException):
            return -1

    def _find_port(self):
        # Finds the serial port names
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i+1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/ttyUSB*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.usbserial*')
        else:
            raise EnvironmentError('Error finding ports on your operating system')

        controller_port = ""
        for port in ports:
            if self._check_port(port) is True:
                controller_port = port
                break

        if controller_port == "":
            raise OSError('Cannot find MTD69x port')
        else:
            return controller_port

    def close(self):
        self._ser.close()

    @staticmethod
    def _response_to_float(response):
        try:
            response = response.replace(']', '').replace('[', '').replace('*', '')
            result = float(response)
            return result
        except Exception:
            raise Exception("Could convert response value to float")

    def _send_query(self, query):
        self._ser.flushInput()
        self._ser.write((query + '\n\r').encode('utf-8'))
        if self._compatible:
            result = self._ser.read_until(b'*').decode('ascii')
        else:
            result = self._ser.read_until(b'>').decode('ascii')

        if result == '' or result == self._error_character:
            return self.FAIL

        return result[:-1]

    def _send_command(self, command, value):
        self._ser.flushInput()
        self._ser.write((command + str(value) + '\n\r').encode('utf-8'))
        if self._compatible:
            result = self._ser.read_until(b'*').decode('ascii')
            if result == '*' or result.startswith('[') or "RESTORE" in result:
                return self.SUCCESS
            else:
                return self.FAIL
        else:
            result = self._ser.read_until(b'>').decode('ascii')
            if result == '>' or result.startswith('['):
                return self.SUCCESS
            else:
                return self.FAIL

    def get_available_commands(self):
        result = self._send_query('?')
        result = result.replace('\r', '\r\n')
        print(result)
        self._commands = result.split('\r\n')

    def restore_all(self):
        return self._send_command('RESTORE', '')
        # return self.send_command('E=', 0) %Alternative command

    def set_echo_off(self):
        if self._compatible:
            return self._send_command('E', 0)
        else:
            return self._send_command('ECHO=', 0)
        # return self.send_command('E=', 0) %Alternative command

## NOT IMPLEMENTED.
## Implementing it implies change to the code, to parse the echo response
    # def set_echo_on(self):
    #     if self.compatible:
    #         self.send_command('E', 1)
    #     else:
    #         self.send_command('ECHO=', 1)
    #     # return self.send_command('E=', 1) %Alternative command

    def get_echo_status(self):
        result = self._send_query('ECHO?')
        if "Echo Off" in result:
            return self.ECHO_OFF
        elif "Echo On" in result:
            return self.ECHO_ON
        else:
            return -1

    def get_id(self):
        if self._compatible:
            result = self._send_query('I')
        else:
            result = self._send_query('ID?')

        result = (result[3:-3]).replace('\r', '\r\n')
        print(result)
        result = result.split('\r\n')
        self._model = result[0]
        self._firmaware_version = result[1].split(': ')[1]
        self._voltage_range = result[2].split(': ')[1]
        self._serial_number = result[3].split(':')[1]
        self._name = result[4].split(':')[1]

    # def get_firmware(self):
    #    return self.send_query('I?')

    def get_name(self):
        name = self._send_query('FRIENDLY?')
        self._name = name.replace('\r>', '')
        return self._name

    def set_name(self, name):
        return self._send_command('FRIENDLY=', name)

    def get_serial_number(self):
        result = self._send_query('SERIAL?')
        self._serial_number = result[:-2]
        return self._serial_number

    def get_compatibility(self):
        result = self._send_query('cm?')[:-1]
        if "Compatibility Mode On" in result:
            return self.COMPATIBILITY_ON
        elif "Compatibility Mode Off" in result:
            return self.COMPATIBILITY_OFF
        else:
            return self.FAIL

    def get_switch_limit(self):
        if self._compatible:
            result = self._send_query('%')[:-1]
        else:
            result = self._send_query('VLIMIT?')[:-1]

        return self._response_to_float(result)

    def get_rotary_mode(self):
        result = self._send_query('ROTARYMODE?')[:-1]
        result = int(result)
        if result is self.ROTARY_MODE_DEFAULT:
            return self.ROTARY_MODE_DEFAULT
        elif result is self.ROTARY_MODE_FINE:
            return self.ROTARY_MODE_FINE
        elif result is self.ROTARY_MODE_TURN_POT:
            return self.ROTARY_MODE_TURN_POT
        else:
            return self.FAIL

    def set_rotary_mode(self, mode):
        return self._send_command("ROTARYMODE=", mode)

    def enable_push_mode(self):
        result = self._send_command('PUSHDISABLE=', 0)
        return result

    def disable_push_mode(self):
        result = self._send_command('PUSHDISABLE=', 1)
        return result

    def get_push_mode(self):
        result = self._send_query('PUSHDISABLE?')[:-1]
        result = int(result)
        if result is self.PUSH_MODE_OFF:
            return self.PUSH_MODE_OFF
        elif result is self.PUSH_MODE_ON:
            return self.PUSH_MODE_ON
        else:
            return self.FAIL

    def enable_master_scan(self):
        result = self._send_command('MSENABLE=', 1)
        self._master_scan_enabled = 1
        return result

    def disable_master_scan(self):
        result = self._send_command('MSENABLE=', 0)
        master_scan_enabled = 0
        return result

    def get_master_scan_state(self):
        result = self._send_query('MSENABLE?')[:-1]
        result = int(result)
        if result is self.MASTER_SCAN_ON:
            return self.MASTER_SCAN_ON
        elif result is self.MASTER_SCAN_OFF:
            return self.MASTER_SCAN_OFF
        else:
            return self.FAIL

    def set_master_voltage(self, voltage):
        self.get_master_scan_state()
        if self._master_scan_enabled:
            result = self._send_command('MSVOLTAGE=', voltage)
        else:
            print("Master Scan not enabled")
            return 0

        return result

    def get_master_voltage(self):
        result = self._send_query('MSVOLTAGE?')
        result = self._response_to_float(result)
        return result

    def set_intensity(self, intensity):
        if intensity < 0:
            intensity = 0
        elif intensity > 15:
            intensity = 15

        result = self._send_command('INTENSITY=', intensity)
        return result

    def get_intensity(self):
        result = self._send_query('INTENSITY?')[:-1]
        return int(result)

    def set_compatibility_on(self):
        return_value = self._send_command('cm=', 1)
        self._compatible = 1
        self._error_character = '*'
        self._voltage_commands_set = ["XV", "XY", "XZ", "AV"]
        self._voltage_commands_get = ["XR", "YR", "ZR"]
        self._voltage_max_commands_set = ["XH", "YH", "ZH", "SYSMAX="]
        self._voltage_min_commands_set = ["XL", "YL", "ZL", "SYSMIN="]
        self._voltage_max_commands_get = ["XH?", "YH?", "ZH?", "SYSMAX?"]
        self._voltage_min_commands_get = ["XL?", "YL?", "ZL?", "SYSMIN?"]
        return return_value

    def set_compatibility_off(self):
        return_value = self._send_command('cm=', 0)
        self._compatible = 0
        self._error_character = 'CMD_NOT_DEFINED>'
        self._voltage_commands_set = ["XVOLTAGE=", "YVOLTAGE=", "ZVOLTAGE=", "ALLVOLTAGE="]
        self._voltage_commands_get = ["XVOLTAGE?", "YVOLTAGE?", "ZVOLTAGE?"]
        self._voltage_max_commands_set = ["XMAX=", "YMAX=", "ZMAX=", "SYSMAX="]
        self._voltage_min_commands_set = ["XMIN=", "YMIN=", "ZMIN=", "SYSMIN="]
        self._voltage_max_commands_get = ["XMAX?", "YMAX?", "ZMAX?", "SYSMAX?"]
        self._voltage_min_commands_get = ["XMIN?", "YMIN?", "ZMIN?", "SYSMIN?"]
        return return_value

    def get_x_voltage(self):
        value = self._send_query(self._voltage_commands_get[0])
        return self._response_to_float(value)

    def get_y_voltage(self):
        value = self._send_query(self._voltage_commands_get[1])
        return self._response_to_float(value)

    def get_z_voltage(self):
        value = self._send_query(self._voltage_commands_get[2])
        return self._response_to_float(value)

    def set_x_voltage(self, voltage):
        return self._send_command(self._voltage_commands_set[0], voltage)

    def set_y_voltage(self, voltage):
        return self._send_command(self._voltage_commands_set[1], voltage)

    def set_z_voltage(self, voltage):
        return self._send_command(self._voltage_commands_set[2], voltage)

    def set_all_voltage(self, voltage):
        return self._send_command(self._voltage_commands_set[3], voltage)

    def set_xyz_voltage(self, voltage_x, voltage_y, voltage_z):
        return self._send_command("XYZVOLTAGE=", str("%.4f,%.4f,%.4f" % (voltage_x, voltage_y, voltage_z)))

    def get_xyz_voltage(self):
        result = self._send_query("XYZVOLTAGE?")
        result = result.replace("[ ", "").replace("]", "").replace("\r", "").replace(" ", "")
        result = result.split(",")
        result = [float(i) for i in result]
        return result

    def get_x_voltage_max(self):
        value = self._send_query(self._voltage_max_commands_get[0])
        return self._response_to_float(value)

    def get_x_voltage_min(self):
        value = self._send_query(self._voltage_min_commands_get[0])
        return self._response_to_float(value)

    def get_y_voltage_max(self):
        value = self._send_query(self._voltage_max_commands_get[1])
        return self._response_to_float(value)

    def get_y_voltage_min(self):
        value = self._send_query(self._voltage_min_commands_get[1])
        return self._response_to_float(value)

    def get_z_voltage_max(self):
        value = self._send_query(self._voltage_max_commands_get[2])
        return self._response_to_float(value)

    def get_z_voltage_min(self):
        value = self._send_query(self._voltage_min_commands_get[2])
        return self._response_to_float(value)

    def get_sys_voltage_max(self):
        value = self._send_query(self._voltage_max_commands_get[3])
        return self._response_to_float(value)

    def get_sys_voltage_min(self):
        value = self._send_query(self._voltage_min_commands_get[2])
        return self._response_to_float(value)

    def set_x_voltage_max(self, voltage):
        return self._send_command(self._voltage_max_commands_set[0], voltage)

    def set_x_voltage_min(self, voltage):
        return self._send_command(self._voltage_min_commands_set[0], voltage)

    def set_y_voltage_max(self, voltage):
        return self._send_command(self._voltage_max_commands_set[1], voltage)

    def set_y_voltage_min(self, voltage):
        return self._send_command(self._voltage_min_commands_set[1], voltage)

    def set_z_voltage_max(self, voltage):
        return self._send_command(self._voltage_max_commands_set[2], voltage)

    def set_z_voltage_min(self, voltage):
        return self._send_command(self._voltage_min_commands_set[2], voltage)

    def set_sys_voltage_max(self, voltage):
        return self._send_command(self._voltage_max_commands_set[3], voltage)

    def set_z_voltage_min(self, voltage):
        return self._send_command(self._voltage_min_commands_set[3], voltage)


if __name__ == '__main__':
    print("MTD69X Piezo controller")