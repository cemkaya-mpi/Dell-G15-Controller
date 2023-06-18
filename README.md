# Dell-G15-Controller
Using this **may** break AWCC on windows. Use at your own risk.

An insanely simple GUI app written in PyQt to control keyboard backlight, power mode and fan speed on Dell G15 (5525) Laptops. Untested on any other laptop, but keyboard part can most likely be used with models that have the ```Bus *** Device ***: ID 187c:0550 Alienware Corporation LED controller```. Power related functions are specific to Dell G15 (5525), but might work on similar models.

By default, leds will flash red on low battery, and have half brightness on battery.

Only static color and morph is supported at this time.

## Installation
You can install from the AUR if on Arch Linux.

Otherwise, no installation necessary, besides installing python dependencies, and creating the udev rule ```/etc/udev/rules.d/00-aw-elc.rules```, and rebooting. Make sure the user is part of the ```plugdev``` group. Alternatively, run the script as root (not recommended).

```
/etc/udev/rules.d/00-aw-elc.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="187c", ATTRS{idProduct}=="0550", MODE="0660", GROUP="plugdev", SYMLINK+="awelc"
```

Polkit is required for power and fan related functionality.


## Screenshots
![](window.png)
## Usage
```
python main.py
```

## License
GNU GENERAL PUBLIC LICENSE v3

## Contributions
Written using the information and code from https://github.com/trackmastersteve/alienfx/issues/41. 

Many thanks to @AlexIII and @T-Troll for their help with the ACPI calls.

