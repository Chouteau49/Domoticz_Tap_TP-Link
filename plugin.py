#           Tapo TP-Link Plugin
#
#           Author:     chout_dev, 2022
#           GNU license
#
"""
<plugin key="tapo_tp-link" name="Tapo TP-Link" author="chout_dev" version="1.0.0">
    <description>
        <h2> Plugin Tapo TP-Link </h2>
        <br/>
        <br/>
        <h3> Appareils pris en charge </h3>
        <br/>
        <ul  style= "list-style-type:square " >
            <li> Prise P100 </li>
            <li> Prise P110 </li>
            <li> Ampoule L530 </li>
        </ul>
    </description>
    <params>
        <param field="Username" label="Username" width="200px" required="true" default=""/>
        <param field="Password" label="Password" width="200px" required="true" default="" password="true"/> -->
        <param field="Address" label="IP or named address" width="200px" required="true" default="192.168.1.*"/>
        <param field="Mode1" label="Type de prise" width="100px">
            <options>
                <option label="P100" value="P100" default="true"/>
                <option label="P110" value="P110"/>
                <option label="L530" value="L530"/>
            </options>
        </param>
        <param  field= "Mode2"  label= "Debug">
            <description><h3> Débogage </h3> Sélectionnez le niveau de messagerie de débogage souhaité </description>
            <options>
                <option  label= "True" value= "Debug"  />
                <option  label= "False" value= "Normal" default= "true"/>
            </options>
        </param>
    </params>
</plugin>
"""

# https://www.domoticz.com/wiki/Developing_a_Python_plugin
from base64 import b64decode

import Domoticz

from PyP100 import PyP100
from PyP100 import PyP110
from PyP100 import PyL530

PRISE_P100 = "P100"
PRISE_P110 = "P110"
PRISE_L530 = "L530"

class BasePlugin:
    enabled = False

    def __init__(self):
        self.tapo = None
        self.unit = 1
        return


    def onStart(self):
        Domoticz.Debug("onStart called")
        self.ip_appareil = Parameters["Address"]
        self.email = Parameters["Username"]
        self.pwd = Parameters["Password"]
        self.type_appareil = Parameters["Mode1"]
        self.debug = Parameters["Mode2"]

        # Setting up debug mode
        if (self.debug not in "Normal"):
            Domoticz.Debugging(1)
            Domoticz.Debug("Debug mode enabled")
        try:
            if self.type_appareil == PRISE_P100:
                self.tapo = PyP100.P100(self.ip_appareil, self.email, self.pwd)
            if self.type_appareil == PRISE_P110:
                self.tapo = PyP110.P110(self.ip_appareil, self.email, self.pwd)
            if self.type_appareil == PRISE_L530:
                self.tapo = PyL530.L530(self.ip_appareil, self.email, self.pwd)

            self.tapo.handshake()  # Creates the cookies required for further methods
            self.tapo.login()  # Sends credentials to the plug and creates AES Key and IV for further methods
            device_info = self.tapo.getDeviceInfo()
            Domoticz.Debug(f"Tapo {PRISE_P100} device info: {self.tapo.getDeviceInfo()}")

            # Getting last state to get device type
            self.update(False)

            # Creating device
            if self.unit not in Devices:
                typeName = "Selector Switch"
                switchType = 0

                encodedName = device_info["result"]["nickname"]
                name = b64decode(encodedName)
                name = name.decode("utf-8")

                Domoticz.Device(
                    Name=name,
                    Unit=self.unit,
                    TypeName=typeName,
                    Switchtype=switchType,
                    Image=1,
                    Options={}).Create()

            self.update()

            DumpConfigToLog()
        except:
            Domoticz.Error("Error create object Tapo")

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(
            Command) + "', Level: " + str(Level))
        if Unit != self.unit:
            Domoticz.Error("Unknown device with unit: " + str(Unit))
            return

        commandValue = 1 if Command == "On" else 0
        if self.lastState["device_on"] == commandValue:
            Domoticz.Log("Command and last state is the same, nothing to do")
            return

        if Command == "On":
            self.tapo.turnOn()
        else:
            self.tapo.turnOff()
        self.update()

        return

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug(
            "Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
                Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

    def update(self, updateDomoticz=True):
        # Domoticz.Debug(f"Debug tapo object value self.tapo vin update => {self.tapo}")
        # self.tapo.handshake()
        # self.tapo.login()
        deviceInfo = self.tapo.getDeviceInfo()

        if deviceInfo["error_code"] != 0:
            self.lastState = None
            Domoticz.Error("Cannot get last state from device error code: " + str(deviceInfo["error_code"]))
        else:
            self.lastState = deviceInfo["result"]
            Domoticz.Debug(self.lastState)

        # Update device
        if self.unit not in Devices or not updateDomoticz:
            return
        powerState = self.lastState["device_on"]
        powerStateValue = 1 if powerState else 0
        powerStateStr = "On" if powerState else "Off"
        if (Devices[self.unit].nValue != powerStateValue) or (Devices[self.unit].sValue != powerStateStr):
            Domoticz.Debug("Updating %s (%d, %s)" % (Devices[self.unit].Name, powerStateValue, powerStateStr))
            Devices[self.unit].Update(nValue=powerStateValue, sValue=powerStateStr)

        return


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device Image:     '" + str(Devices[x].Image) + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
