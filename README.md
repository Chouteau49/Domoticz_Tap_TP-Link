# Domoticz_Tapo_TP-Link
Plugin TP-Link Tapo for Domoticz.

This version only supports the creation of on/off switches.
Tested with the Tapo P100 and Tapo P110 smart plug device.

## Prerequisites

Have created your account on the Tapo application and added your connected objects to the application.

Then to retrieve the ip address of your device, go to settings / device info / IP address

## Installation

Connect to your Domoticz server via SSH and go to Domoticz's plugins directory. (Example : cd /opt/domoticz/config/plugins/)
Clone this repository into the plugins directory:

```
sudo git clone https://github.com/Chouteau49/Domoticz_Tapo_TP-Link.git
```

Restart Domoticz

## Configuration

On Domoticz, Configuration / Hardware => Add a new
In the Type list choose Tapo TP-Link.

Fill in the device email, password and IP values.

## Authors

* **Guillaume Zin** - *Initial work* - [Domoticz_Tapo_TP-Link](https://github.com/Chouteau49/Domoticz_Tapo_TP-Link)

See also the list of [contributors](https://github.com/Chouteau49/Domoticz_Tapo_TP-Linkcontributors) who participated in this project.

## License

This project is licensed under the MIT license - see the [LICENSE](LICENSE) file for details