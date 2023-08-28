#!/bin/python
import sys
import pexpect
import tempfile
import awelc
import PySide6
from PySide6.QtCore import (QSettings, QTimer)
from PySide6.QtGui import (QIcon, QAction)
from PySide6.QtWidgets import (QMessageBox,QGridLayout, QGroupBox, QWidget, QPushButton, QApplication,
                               QVBoxLayout, QHBoxLayout, QDialog, QSlider, QLabel, QSystemTrayIcon, QMenu, QComboBox)


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        try:
            self.logfile = open("/tmp/dellg15controller.log","w")
            sys.stdout = self.logfile
        except:
            print("Exception trying to open /tmp/dellg15controller.log")
            exit()
        print("Log file:{}".format(self.logfile))
        self.logfile.write("test")
        self.init_acpi_call()
        self.setMinimumWidth(500)
        self.setWindowTitle("Dell G15 Controller")
        # Read last choices from QSettings
        self.settings = QSettings('Dell-G15', 'Controller')
        #Create grid layout
        grid = QGridLayout()
        self.timer = None
        if (self.is_plugdev):
            grid.addWidget(self.createFirstExclusiveGroup(), 0, 0)
        if (self.is_root and self.is_dell_g15):
            grid.addWidget(self.createSecondExclusiveGroup(), 0, 1)
            self.timer = QTimer(self)    #timer to update fan rpm values
            self.timer.setInterval(1000)
            self.timer.timeout.connect(self.get_rpm_and_temp)
            self.timer.start()
        self.setLayout(grid)

    def init_acpi_call(self):
        self.power_modes_dict = {
            "USTT_Balanced" : "0xa0",
            "USTT_Performance" : "0xa1",
            # "USTT_Cool" : "0xa2",   #Does not work
            "USTT_Quiet" : "0xa3",
            "USTT_FullSpeed" : "0xa4",
            "USTT_BatterySaver" : "0xa5",
            "G Mode" : "0xab",
            "Manual" : "0x0",
        }
        self.acpi_call_dict = {
            "get_laptop_model" : ["0x1a", "0x02", "0x02"],
            "get_power_mode" : ["0x14", "0x0b", "0x00"],
            "set_power_mode" : ["0x15", "0x01"],    #To be used with a parameter
            "toggle_G_mode" : ["0x25", "0x01"],
            "get_G_mode" : ["0x25", "0x02"],
            "set_fan1_boost" : ["0x15", "0x02", "0x32"],            #To be used with a parameter
            "get_fan1_boost" : ["0x14", "0x0c", "0x32"],
            "get_fan1_rpm" : ["0x14", "0x05", "0x32"],
            "get_cpu_temp" : ["0x14", "0x04", "0x01"],
            "set_fan2_boost" : ["0x15", "0x02", "0x33"],            #To be used with a parameter
            "get_fan2_boost" : ["0x14", "0x0c", "0x33"],
            "get_fan2_rpm" : ["0x14", "0x05", "0x33"],
            "get_gpu_temp" : ["0x14", "0x04", "0x06"]
        }
        self.acpi_cmd = "echo \"\\_SB.AMW3.WMAX 0 {} {{{}, {}, {}, 0x00}}\" > /proc/acpi/call; cat /proc/acpi/call"
        
        print("Attempting to create elevated bash subprocess.")
        # Create a shell subprocess (root needed for power related functions)
        self.shell = pexpect.spawn('bash', encoding='utf-8', logfile=self.logfile)
        self.shell.expect("[#$] ")
        # Check if user is member of plugdev
        self.is_plugdev = (self.shell_exec("groups")[1].find("plugdev") != -1)
        if self.is_plugdev:
            print("User is member of group of plugdev.")
        else:
            choice = QMessageBox.question(self,"Warning","User is not a member of group plugdev. Try to enable keyboard backlight control anyway?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            self.is_plugdev = (choice == QMessageBox.StandardButton.Yes) #User override
        #Elevate privileges (pkexec is needed)
        self.shell_exec("pkexec")
        #Check if root or not
        self.is_root = (self.shell_exec("whoami")[1].find("root") != -1)
        if self.is_root:
            print("Bash shell is root. Enabling ACPI methods...")
            # Check laptop model and inform user if model is not supported.
            self.is_dell_g15 = (self.acpi_call("get_laptop_model") == "0x12c0")
            if self.is_dell_g15:
                print("Laptop model is supported.")
            else:
                choice = QMessageBox.question(self,"Unrecognized laptop","Laptop model is NOT supported. Try ACPI methods anyway? You might damage your hardware. Please do not do this if you don't know what you are doing!",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                self.is_dell_g15 = (choice == QMessageBox.StandardButton.Yes) #User override
        else:
            print("Bash shell is NOT root. Disabling ACPI methods...")
            popup = QMessageBox.information(self,"Warning","No root access. Power related functions will not work, and will not be displayed.")
        
    def createFirstExclusiveGroup(self):
        groupBox = QGroupBox("Keyboard Led")
        vbox = QVBoxLayout()
        
        self.state = (self.settings.value("State", "Off"))
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
        self.duration_label = QLabel("Duration")
        self.duration = QSlider(orientation=PySide6.QtCore.Qt.Orientation(0x01))
        self.duration.setMinimum(0x4)
        self.duration.setMaximum(0xfff)
        self.duration.setValue(int(self.settings.value("Duration", 255)))
        widget = QWidget()
        hbox = QHBoxLayout(widget)
        self.combobox_mode = QComboBox()
        self.combobox_mode.addItems(["Static Color", "Morph", "Color and Morph", "Off"])
        self.combobox_mode.setCurrentText(self.settings.value("Action", "Static Color"))

        self.button_apply = QPushButton("Apply")
        hbox.addWidget(self.combobox_mode)
        hbox.addWidget(self.button_apply)
        
        # Add widgets to layout
        vbox.addWidget(self.red_label)
        vbox.addWidget(self.red)
        vbox.addWidget(self.green_label)
        vbox.addWidget(self.green)
        vbox.addWidget(self.blue_label)
        vbox.addWidget(self.blue)
        vbox.addWidget(self.duration_label)
        vbox.addWidget(self.duration)
        vbox.addWidget(widget)

        # Add button callbacks
        self.combobox_mode.currentTextChanged.connect(self.combobox_choice)
        self.button_apply.clicked.connect(self.apply_leds)
        
        #Return
        groupBox.setLayout(vbox)
        return groupBox

    def createSecondExclusiveGroup(self):
        groupBox = QGroupBox("Power and Fans")
        vbox = QVBoxLayout()
        
        widget = QWidget()
        hbox = QHBoxLayout(widget)
        
        #Power mode choice and Apply button
        self.combobox_mode_power = QComboBox()
        self.combobox_mode_power.addItems(self.power_modes_dict.keys())
        self.combobox_mode_power.setCurrentText(self.settings.value("Power", "USTT_Balanced"))
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        
        #Fan 1 RPM
        self.fan1_label = QLabel("CPU Fan Boost")
        widget_fan1 = QWidget()
        hbox_fan1 = QHBoxLayout(widget_fan1)
        self.fan1_boost = QSlider(orientation=PySide6.QtCore.Qt.Orientation(0x01))
        self.fan1_boost.setMinimum(0x00)
        self.fan1_boost.setMaximum(0xff)
        self.fan1_boost.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fan1_boost.setTickInterval(25.5)   #10 steps
        self.fan1_boost.setValue(int(self.settings.value("Fan1 Boost", 0x00)))
        self.fan1_current = QLabel("0 RPM")
        hbox_fan1.addWidget(self.fan1_boost)
        hbox_fan1.addWidget(self.fan1_current)

        #Fan 2 RPM
        self.fan2_label = QLabel("GPU Fan Boost")
        widget_fan2 = QWidget()
        hbox_fan2 = QHBoxLayout(widget_fan2)
        self.fan2_boost = QSlider(orientation=PySide6.QtCore.Qt.Orientation(0x01))
        self.fan2_boost.setMinimum(0x00)
        self.fan2_boost.setMaximum(0xff)
        self.fan2_boost.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fan2_boost.setTickInterval(25.5)   #10 steps
        self.fan2_boost.setValue(int(self.settings.value("Fan2 Boost", 0x00)))
        self.fan2_current = QLabel("0 RPM")
        hbox_fan2.addWidget(self.fan2_boost)
        hbox_fan2.addWidget(self.fan2_current)

        #Add widgets to layout
        vbox.addWidget(self.combobox_mode_power)
        vbox.addWidget(self.fan1_label)
        vbox.addWidget(widget_fan1)
        vbox.addWidget(self.fan2_label)
        vbox.addWidget(widget_fan2)
        vbox.addWidget(self.info_label)
        
        # Add button callbacks
        self.combobox_mode_power.currentTextChanged.connect(self.combobox_power)
        self.fan1_boost.sliderReleased.connect(self.slider_fan1)
        self.fan2_boost.sliderReleased.connect(self.slider_fan2)
        
        #Return
        groupBox.setLayout(vbox)
        return groupBox

    #Callbacks
    def combobox_choice(self):
        self.settings.setValue("Action", self.combobox_mode.currentText())
    
    def apply_leds(self):
        if self.settings.value("Action", "Static Color") == "Static Color":
            self.apply_static()
        elif self.settings.value("Action", "Static Color") == "Morph":
            self.apply_morph()
        elif self.settings.value("Action", "Static Color") == "Color and Morph":
            self.apply_color_and_morph()    
        else:   #Off
            self.remove_animation()
    
    def combobox_power(self):
        self.fan1_boost.setValue(0)
        self.fan2_boost.setValue(0)
        self.settings.setValue("Power", self.combobox_mode_power.currentText())
        choice = self.settings.value("Power", "USTT_Balanced")
        message = ""
        
        # Set power mode
        mode = self.power_modes_dict[choice]
        self.acpi_call("set_power_mode",mode)
        # Get current power mode to confirm
        result = self.acpi_call("get_power_mode")
        if (result == mode):   #Expected result
            message = "Power mode set to {}.\n".format(choice)
        else:
            message = "Error! Command returned: {}, but expecting {}.\n".format(str(result),str(mode))
        # Get G Mode
        result = self.acpi_call("get_G_mode")
        if (choice == "G Mode") != (result == "0x1"):  #Toggle G Mode if needed.
            #Toggle G mode
            result_toggle = self.acpi_call("toggle_G_mode")
            if (("0x1" if choice == "G Mode" else "0x0") != result_toggle): 
                message = message + "Expected to read G Mode = {} but read {}!\n".format(choice == "G Mode",result_toggle)

        self.info_label.setText(message)
    
    def slider_fan1(self):
        #Fan1 has id 0x32
        #Get current fan boost
        fan1_last_boost = self.acpi_call("get_fan1_boost")
        #Set new fan boost
        new_val = self.fan1_boost.value()
        self.acpi_call("set_fan1_boost","0x{:2X}".format(new_val))
        #Get current fan boost
        fan1_new_boost = self.acpi_call("get_fan1_boost")
        self.info_label.setText("Fan1 Boost: {:.0f}% to {:.0f}%.".format(int(fan1_last_boost,0)/0xff*100,int(fan1_new_boost,0)/0xff*100))
    
    def slider_fan2(self):
        #Fan2 has id 0x33
        #Get current fan boost
        fan2_last_boost = self.acpi_call("get_fan2_boost")
        #Set new fan boost
        new_val = self.fan2_boost.value()
        self.acpi_call("set_fan2_boost","0x{:2X}".format(new_val))
        #Get current fan boost
        fan2_new_boost = self.acpi_call("get_fan2_boost")
        self.info_label.setText("Fan2 Boost: {:.0f}% to {:.0f}%.".format(int(fan2_last_boost,0)/0xff*100,int(fan2_new_boost,0)/0xff*100))
    
    def get_rpm_and_temp(self):
        if self.isVisible():
            #Get current rpm and temp
            fan1_rpm = self.acpi_call("get_fan1_rpm")
            cpu_temp = self.acpi_call("get_cpu_temp")
            fan2_rpm = self.acpi_call("get_fan2_rpm")
            gpu_temp = self.acpi_call("get_gpu_temp")
            self.fan1_current.setText("{} RPM, {} °C".format(int(fan1_rpm,0),int(cpu_temp,0)))
            self.fan2_current.setText("{} RPM, {} °C".format(int(fan2_rpm,0),int(gpu_temp,0)))
    # Helper Functions
    
    #Execute given command in elevated shell
    def acpi_call(self, cmd, arg1="0x00", arg2="0x00"):
        args = self.acpi_call_dict[cmd]
        if len(args)==4:
            cmd_current = self.acpi_cmd.format(args[0], args[1], args[2], args[3])
        elif len(args)==3:
            cmd_current = self.acpi_cmd.format(args[0], args[1], args[2], arg1)
        elif len(args)==2:
            cmd_current = self.acpi_cmd.format(args[0], args[1], arg1, arg2)
        else:
            cmd_current=""
        return self.parse_shell_exec(self.shell_exec(cmd_current)[1])   #Return parsed first line

    def shell_exec(self, cmd : str):
        print("Bash: Executing {}".format(cmd))
        self.shell.sendline(cmd)
        self.shell.expect("[#$] ")
        result = self.shell.before
        result = result.split('\n')
        for line in result[1:]: #First line is the command that was sent
            print(line)
        return result

    def parse_shell_exec(self,line:str):
        return line[line.find('\r')+1:line.find('\x00')] #Read between carriage return and end of the line (disregard color)

    # Apply given colors to keyboard.
    def apply_static(self):
        awelc.set_static(self.red.value(), self.green.value(),
                         self.blue.value())
        self.settings.setValue("Action", "Static Color")
        self.settings.setValue("Red", self.red.value())
        self.settings.setValue("Green", self.green.value())
        self.settings.setValue("Blue", self.blue.value())
        self.settings.setValue("Duration", self.duration.value())
        self.settings.setValue("State", "On")

    def apply_morph(self):
        awelc.set_morph(self.red.value(), self.green.value(),
                        self.blue.value(), self.duration.value())
        self.settings.setValue("Action", "Morph")
        self.settings.setValue("Red", self.red.value())
        self.settings.setValue("Green", self.green.value())
        self.settings.setValue("Blue", self.blue.value())
        self.settings.setValue("Duration", self.duration.value())
        self.settings.setValue("State", "On")
    
    def apply_color_and_morph(self):
        awelc.set_color_and_morph(self.red.value(), self.green.value(),
                        self.blue.value(), self.duration.value())
        self.settings.setValue("Action", "Color and Morph")
        self.settings.setValue("Red", self.red.value())
        self.settings.setValue("Green", self.green.value())
        self.settings.setValue("Blue", self.blue.value())
        self.settings.setValue("Duration", self.duration.value())
        self.settings.setValue("State", "On")
    
    def remove_animation(self):
        awelc.remove_animation()
        self.settings.setValue("State", "Off")

    # Apply last action when called from system tray
    def tray_on(self):
        # if self.settings.value("Action", "Static Color") == "Static Color":
        #     self.apply_static()
        # elif self.settings.value("Action", "Static Color") == "Morph":
        #     self.apply_morph()
        # else:  #Off
        #     self.remove_animation()
        awelc.set_dim(0)
        self.settings.setValue("State", "On")


    def tray_off(self):
        # awelc.set_static(0, 0, 0)
        # awelc.remove_animation()
        awelc.set_dim(100)
        self.settings.setValue("State", "Off")


class TrayIcon(QSystemTrayIcon):

    def __init__(self, window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = QSettings('Dell-G15', 'Controller')
        self.state = (self.settings.value("State", "Off"))
        self.activated.connect(self.toggle_leds)
        self.window = window

    def toggle_leds(self, reason):
        if self.settings.value("State", "Off") == "Off":
            self.settings.setValue("State", "On")
            self.window.tray_on()
        else:
            self.settings.setValue("State", "Off")
            self.window.tray_off()

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    icon = QIcon.fromTheme("alienarena")
    app.setWindowIcon(icon)
    app.setQuitOnLastWindowClosed(False)

    # Create and show the window
    window = MainWindow()
    window.show()

    # Add item on the system tray
    tray = TrayIcon(window)
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.setToolTip("Right click to see the menu. Left click to toggle leds.")

    # System tray options
    menu = QMenu()
    show = QAction("Show Window")
    boost_on = QAction("Boost on")
    boost_off = QAction("Boost off")
    quit = QAction("Quit")
    menu.addAction(show)
    menu.addAction(quit)
    # Adding options to the System Tray
    tray.setContextMenu(menu)

    # Register callbacks
    quit.triggered.connect(app.quit)
    show.triggered.connect(window.show)

    # Run the main Qt loop
    sys.exit(app.exec())
