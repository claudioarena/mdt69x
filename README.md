# mdt69x

This is a simple Python module to communicate with Thorlabs MDT69X Piezo controllers.

### Getting Started

Simply copy the [mdt69x.py](mdt69x/mdt69x.py) in your project directory.
The module uses the pySerial module to communicate over USB with the controller, so make sure to add it to your project as well.

Alternatively, install the module by running:

```
pip install mdt69x
```


### Details

The module implements almost all commands supported by the Thorlabs MDT693 controller.
The only commands not implemented are DACSTEP (both get and set), and the arrow commands (up, down, right, left).

An example file is provided ([mdt69x_example.py](examples/mdt69x_example.py)), which shows usage of a few of the available methods.


The module was tested with the Thorlabs MDT693, but it should also work with the other MDT69X modules.

It works both with and without compatibility mode,
although it defaults to compatibility mode.
Note that certain commands (such as set_xyz_voltage) will only work on firmware version >2,
 and will not work if you try to use them on compatible hardware/firmware.

## Author

* **Claudio Arena** - University College London (UCL), Astrophysics PhD 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
