#!/bin/python
import awelc
import sys
import PySide6
from PySide6.QtCore import (QSettings)
from PySide6.QtGui import (QIcon, QAction)
from PySide6.QtWidgets import (QPushButton, QApplication,
                               QVBoxLayout, QDialog, QSlider, QLabel, QSystemTrayIcon, QMenu)


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Read last choices from QSettings
        self.settings = QSettings('Dell-G15', 'LedControl')
        self.state = (self.settings.value("State", "Off"))
        self.action = (self.settings.value("Action", "static"))
        # Create widgets
        self.red_label = QLabel("Red")
        self.red = QSlider(orientation=PySide6.QtCore.Qt.Orientation(0x01))
        # self.red.setTickPosition(QSlider.TickPosition(0x3))
        # self.red.setTickInterval(1)
        # self.red.setSingleStep(1)
        self.red.setMinimum(0)
        self.red.setMaximum(255)
        self.red.setValue(int(self.settings.value("Red", 122)))
        # self.red.valueChanged.connect(self.value_changed_red)
        self.green_label = QLabel("Green")
        self.green = QSlider(orientation=PySide6.QtCore.Qt.Orientation(0x01))
        self.green.setMinimum(0)
        self.green.setMaximum(255)
        self.green.setValue(int(self.settings.value("Green", 122)))
        self.blue_label = QLabel("Blue")
        self.blue = QSlider(orientation=PySide6.QtCore.Qt.Orientation(0x01))
        self.blue.setMinimum(0)
        self.blue.setMaximum(255)
        self.blue.setValue(int(self.settings.value("Blue", 122)))
        self.duration_label = QLabel("Tempo")
        self.duration = QSlider(
            orientation=PySide6.QtCore.Qt.Orientation(0x01))
        self.duration.setMinimum(0x4)
        # self.duration.setMinimum(awelc.DURATION_MIN)
        self.duration.setMaximum(0xfff)
        self.duration.setValue(int(self.settings.value("Duration", 255)))
        # self.duration.setMaximum(awelc.DURATION_MAX)
        self.button_static = QPushButton("Static Color")
        self.button_morph = QPushButton("Morph")
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.red_label)
        layout.addWidget(self.red)
        layout.addWidget(self.green_label)
        layout.addWidget(self.green)
        layout.addWidget(self.blue_label)
        layout.addWidget(self.blue)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration)
        layout.addWidget(self.button_static)
        layout.addWidget(self.button_morph)
        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.button_static.clicked.connect(self.apply_static)
        self.button_morph.clicked.connect(self.apply_morph)

    # Apply given colors to keyboard.
    def apply_static(self):
        awelc.set_static(self.red.value(), self.green.value(),
                         self.blue.value())
        self.action = "static"
        self.settings.setValue("Red", self.red.value())
        self.settings.setValue("Green", self.green.value())
        self.settings.setValue("Blue", self.blue.value())
        self.settings.setValue("Duration", self.duration.value())
        self.settings.setValue("State", "On")

    def apply_morph(self):
        # print(
        #     f"Red:{self.red.value()},Green:{self.green.value()},Blue:{self.blue.value()}")
        # print(f"Duration:{self.duration.value()}")
        awelc.set_morph(self.red.value(), self.green.value(),
                        self.blue.value(), self.duration.value())
        self.action = "morph"
        self.settings.setValue("Red", self.red.value())
        self.settings.setValue("Green", self.green.value())
        self.settings.setValue("Blue", self.blue.value())
        self.settings.setValue("Duration", self.duration.value())
        self.settings.setValue("State", "On")

    # Apply last action when called from system tray
    def tray_on(self):
        if self.action == 'static':
            self.apply_static()
        else:  # morph
            self.apply_morph()
        self.settings.setValue("State", "On")

    def tray_off(self):
        awelc.set_static(0, 0, 0)
        self.settings.setValue("State", "Off")


class TrayIcon(QSystemTrayIcon):

    def __init__(self, form, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = QSettings('Dell-G15', 'LedControl')
        self.state = (self.settings.value("State", "Off"))
        self.activated.connect(self.toggle_leds)

    def toggle_leds(self, reason):
        if self.settings.value("State", "Off") == "Off":
            self.settings.setValue("State", "On")
            form.tray_on()
        else:
            self.settings.setValue("State", "Off")
            form.tray_off()


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("alien.svg"))
    app.setQuitOnLastWindowClosed(False)

    # Create and show the window
    form = Form()
    form.show()

    # Add item on the system tray
    icon = QIcon("alien.svg")  # Add an icon
    tray = TrayIcon(form)
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.setToolTip("Right click to see the menu. Left click to toggle leds.")

    # System tray options
    menu = QMenu()
    quit = QAction("Quit")
    menu.addAction(quit)
    # Adding options to the System Tray
    tray.setContextMenu(menu)

    # Register callbacks
    quit.triggered.connect(app.quit)

    # Run the main Qt loop
    sys.exit(app.exec())
