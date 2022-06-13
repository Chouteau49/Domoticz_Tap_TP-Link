#           Tapo TP-Link Plugin
#
#           Author:     chout_dev, 2022
#           GNU license
#
"""
<plugin key="tapo_tp-link" name="Tapo TP-Link" author="chout_dev" version="1.0.0" externallink="https://github.com/Chouteau49/Domoticz_Tap_TP-Link.git">
    <description>
        <h2> Plugin Tapo TP-Link </h2><br/>
        <h3> Appareils </h3>
        <ul  style= "list-style-type:square " >
            <li> Prise P100 </li>
            <li> Prise P110 </li>
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
            </options>
        </param>
        <param  field= "Mode2"  label= "Debug"  width= "75px" >
            <description><h2> Débogage </h2> Sélectionnez le niveau de messagerie de débogage souhaité </description>
            <options>
                <option  label= "True" value= "Debug" />
                <option  label= "False" value= "Normal"   default= "False"  />
            </options>
        </param>
    </params>
</plugin>
"""

# https://www.domoticz.com/wiki/Developing_a_Python_plugin
import Domoticz
from Domoticz import Devices, Parameters

from PyP100 import PyP100

PRISE_P100 = "P100"

class BasePlugin:
    enabled = False

    def __init__(self):
        self.ip_appareil = Parameters["Address"]
        self.email = Parameters["Username"]
        self.pwd = Parameters["Password"]
        self.type_appareil = Parameters["Mode1"]
        self.debug = Parameters["Mode2"]
        self.tapo = None
        return


    def onStart(self):

        # Setting up debug mode
        if (self.debug is not False):
            Domoticz.Debugging(1)
            Domoticz.Debug("Debug mode enabled")

        Domoticz.Log("onStart called")
        if self.type_appareil == PRISE_P100:
            Domoticz.Debug(f"Tapo object {PRISE_P100} created with IP: {self.ip_appareil}")
            self.tapo = PyP100.P100(self.ip_appareil, self.email, self.pwd) #Creating a P100 plug object

        self.tapo.handshake()  # Creates the cookies required for further methods
        self.tapo.login()  # Sends credentials to the plug and creates AES Key and IV for further methods
        Domoticz.Debug(f"Tapo {PRISE_P100} device info: {self.tapo.getDeviceInfo()}")

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(
            Command) + "', Level: " + str(Level))
        if Unit != self.unit:
            Domoticz.Error("Unknown device with unit: " + str(Unit))
            return

        commandValue = 1 if Command == "On" else 0
        if self.lastState["device_on"] == commandValue:
            Domoticz.Log("Command and last state is the same, nothing to do")
            return

        self.tapo.handshake()
        self.tapo.login()
        if Command == "On":
            self.tapo.turnOn()
        else:
            self.tapo.turnOff()
        self.update()

        return

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log(
            "Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
                Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")


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
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
