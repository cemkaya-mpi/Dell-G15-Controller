# Dell-G15-LedControl
Using this **may** break AWCC on windows.

An insanely simple GUI app written in PyQt to control keyboard brightness and color on Dell G15 (5525) Laptops. Untested on any other laptop, but can most likely be used with models that have the ```Bus *** Device ***: ID 187c:0550 Alienware Corporation LED controller```

By default, leds will flash red on low battery, and have half brightness on battery.

Only static color and morph is supported at this time.

## Installation
You can install from the AUR if on Arch Linux.

Otherwise, no installation necessary, besides creating the udev rule ```/etc/udev/rules.d/00-aw-elc.rules```, and rebooting. Make sure the user is part of the ```plugdev``` group. Alternatively, run the script as root (not recommended).

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="187c", ATTRS{idProduct}=="0550", MODE="0660", GROUP="plugdev", SYMLINK+="awelc"
```
## Screenshots
![](window.png)
## Usage
```
python main.py
```

## License
GNU GENERAL PUBLIC LICENSE v3

## Contributions
Written using the information and code from https://github.com/trackmastersteve/alienfx/issues/41. Please let me know if you'd like this repository removed, or have suggestions and improvements.